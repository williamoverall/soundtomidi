"""Sound To MIDI. Takes live audio and generates MIDI information from it.

Main loop for sound to MIDI processing. Takes audio samples in and shares
information with audio feature processors.

Usage:
  soundtomidi.py [options]

Options:
  -h --help                     Show this screen.
  --listsounddevices            List available sound devices.
  --listmidiports               List MIDI ports.
  --writeinifile                Write options to ini file, as specified by
                                inifile option. If the file already present,
                                a backup is made of original.
  --inifile=FILE                Name of options settings file.
                                [default: soundtomidi.ini]
  --inputdevice=DEVICE          ID of the sound input device. System default
                                audio input device will be used if not
                                specified.
                                [default: default]
  --channels=CHANNELS           Number of channels to capture.
                                [default: 1]
  --samplerate=SAMPLERATE       Capture rate for audio samples.
                                [default: 44100]
  --framesize=FRAMESIZE         Size of each frame captured.
                                [default: 512]
  --gettempo=TEMPO              Get the tempo of the audio.
                                [default: True]
  --getbeats=BEATS              Get the beats of the audio.
                                [default: True]
  --balg=BALG                   Aubio algorithm to use for the beat.
                                [default: default]
  --bframemult=BFRAMEMULT       Number of frames to use in calculation.
                                [default: 1]
  --bhopmult=BHOPMULT           Hop size, as percent of FRAMEMULT.
                                [default: 1]
  --badjust=BADJUST             Adjust the incoming beats to match reality.
                                Used to deal with beat detector seeing every
                                other beat (or twice as many as there are).
                                ".5" inserts beat halfway between two detected
                                beats, "2" sends one beat message for every
                                two detected, and "1" makes no adjustment.
                                (Not yet implemented)
                                [default: 1]
  --bcontrolnum=BCONTROLNUM     Controller number to send beat messages.
                                If "None", no control messages will be sent.
                                [default: 15]
  --bsysexnum=BSYSEXNUM         Prefix to send prior to beat number
                                in sysex messages.
                                If "None", no sysex messages will be sent.
                                [default: 0x1B]
  --bvaltype=BVALTYPE           Type of value to send with beat
                                controller or sysex message.
                                Any arbitrary number 0-127, or a
                                comma separated looping listing of
                                values to send. For example,
                                "0,1,2,3" will send "0" for the first
                                beat, "3" for fourth beat, then back to
                                "0" for the next one.
                                [default: 0,1,2,3,4,5,6,7]
  --bclock=BCLOCK               Send 24 clock ticks messages after each beat.
                                (Not yet implemented)
                                [default: False]
  --getrms=RMS                  Get the RMS.
                                [default: True]
  --getfrequencies=FREQS        Get the strength of filtered frequencies.
                                [default: True]
  --getpitch=PITCHES            Get the fundamental pitch of the audio.
                                [default: True]
  --sendmidi=MIDI               Send MIDI messages?
                                [default: True]
  --outport=MIDIOUTPORT         Name of the MIDI output port. If left as
                                default, uses first MIDI port found.
                                [default: default]
  --outchannel=OUTCHANNEL       Number of the MIDI channel to send messages on.
                                Valid numbers 1-16.
                                [default: 14]
  --sysexmanf=MANF              Manufacturer prefix code for sysex messages.
                                Int or hex values, separarated by space.
                                [default: 0x7D]

"""
from __future__ import print_function
from __future__ import division
from docopt import docopt
import configparser
import os.path
import time
import sounddevice as sd
from datetime import datetime as dt
import mido
import beat

class Options:
    """Take configuration options as arguments or from an inifile.

    Docopt is used to describe the various configuration options, and
    there are many. This is handy for one off changes, but having a nice
    .ini file, organized by function, makes things a little clearer. This
    class mushes together command line arguments and ini file options into
    an dictionary used throughout the program.

    Other than loading all this up, it also is capable of generating a
    template .ini file organized by section with the defaults from docopt
    already poplulated. The write_options_ini functions could definitely
    be written more efficiently, but at this early stage it is helpful
    to see things listed the long way. Potentially something could tap into
    the docopt library and generate the ini file without even explicitly
    typing all of this out.

    """

    def __init__(self):
        self.settings = docopt(__doc__, version='Sound to MIDI 0.1')
        for key, value in self.settings.items():
            new_key = key[2:]
            self.settings[new_key] = self.settings.pop(key)
        config = configparser.ConfigParser(allow_no_value=True)
        filename = self.settings['inifile']
        if os.path.isfile(filename) and config.read(filename)[0] == filename:
            for section in config.sections():
                for key, value in config.items(section):
                    if value is None:
                        value = True
                    # This is messy right now.  INI files will override default
                    #  or arguments. Should be docopt defaults, which INI can
                    # replace, which arguments can replace.
                    self.settings[key] = value

    def write_options_ini(self):
        config = configparser.ConfigParser(allow_no_value=True)
        config.add_section('soundcard')
        config.set('soundcard', 'inputdevice', self.settings['inputdevice'])
        config.set('soundcard', 'channels', self.settings['channels'])
        config.set('soundcard', 'samplerate', self.settings['samplerate'])
        config.set('soundcard', 'framesize', self.settings['framesize'])
        config.add_section('beats')
        config.set('beats', 'getbeats', self.settings['getbeats'])
        config.set('beats', 'balg', self.settings['balg'])
        config.set('beats', 'bframemult', self.settings['bframemult'])
        config.set('beats', 'bhopmult', self.settings['bhopmult'])
        config.set('beats', 'badjust', self.settings['badjust'])
        config.set('beats', 'bcontrolnum', self.settings['bcontrolnum'])
        config.set('beats', 'bsysexnum', self.settings['bsysexnum'])
        config.set('beats', 'bvaltype', self.settings['bvaltype'])
        config.set('beats', 'bclock', self.settings['bclock'])

        if os.path.exists(self.settings['inifile']):
            os.rename(self.settings['inifile'],
                      self.settings['inifile'] + "." + dt.now().strftime("%s"))
        with open(self.settings['inifile'], 'wb') as configfile:
            config.write(configfile)


class MidiProcessor:
    """Wrapper class for receiving messages and sending out via mido library.

    Sticky object that receives messages from the various audio processing
    classes and MIDIfies them using the mido library.  Deals with
    the custom manufacturer sysex prefix bytes.

    """

    def __init__(self):
        self.midi_outport = None
        self.sysex_prefix = []
        for manf_byte in options.settings['sysexmanf'].split(' '):
            self.sysex_prefix.append(int(manf_byte, 0))
        self.channel = int(options.settings['outchannel']) - 1

    def add_control_message(self, control, value):
        self.send_message(mido.Message('control_change',
                                       channel=self.channel,
                                       control=control,
                                       value=value))

    def add_note_on_message(self, note):
        self.send_message(mido.Message('note_on',
                                       channel=self.channel,
                                       note=note))

    def add_note_off_message(self, note):
        self.send_message(mido.Message('note_off',
                                       channel=self.channel,
                                       note=note))

    def add_sysex_message(self, commands, datas):
        sysexdata = self.sysex_prefix[:]
        for command in commands:
            sysexdata.append(command)
        for data in datas:
            sysexdata.append(data)
        self.send_message(mido.Message('sysex', data=sysexdata))

    def send_message(self, mido_message):
        if self.midi_outport:
            self.midi_outport.send(mido_message)


class ProcessAudio:
    """Primary loop. Take audio frames and deliver to audio processors.

    Using sounddevice audio library, and as configured by options, take
    incoming data from sound card and send a copy of the audio data to
    the audio processors that are turned on.  Responsible for initializing
    the audio processors and midi processor.

    """

    def __init__(self):
        self.midi_processor = MidiProcessor()
        if options.settings['sendmidi']:
            if options.settings['outport'] == 'default':
                available_ports = mido.get_output_names()
                if available_ports:
                    options.settings['outport'] = available_ports[0]
                else:
                    options.settings['outport'] = ""
            if options.settings['outport']:
                self.midi_processor.midi_outport = mido.open_output(
                    options.settings['outport'])

        if options.settings['getbeats'] == 'True':
            self.beat = beat.Beat(options)
            self.beat.midi_processor = self.midi_processor
        else:
            self.beat = None

    def callback(self, data, ignore_frames, ignore_time, ignore_status):
        if any(data):
            if self.beat:
                self.beat.add_frame(data[:, 0])

    def start(self):
        if options.settings['inputdevice'] == 'default':
            options.settings['inputdevice'] = sd.default.device['input']
        with sd.InputStream(device=options.settings['inputdevice'],
                            channels=int(options.settings['channels']),
                            callback=self.callback,
                            blocksize=int(options.settings['framesize']),
                            samplerate=int(options.settings['samplerate'])):
            while True:
                pass


if __name__ == '__main__':
    # Startup loop. Populates options and starts up ProcessAudio.
    #
    # Loads the options class, and if it was one the special cases like
    # writing the inifile or printing out the midi and sound device
    # information, do that then quit.
    #
    # Otherwise, start the ProcessAudio class and get out of the way.
    options = Options()
    if options.settings['writeinifile']:
        options.write_options_ini()
        quit()
    elif options.settings['listsounddevices'] or options.settings[
        'listmidiports']:
        if options.settings['listsounddevices']:
            print("\nAvailable sound devices:")
            print(sd.query_devices())
        if options.settings['listmidiports']:
            print("\nAvailable MIDI ports:")
            print("\n".join(mido.get_output_names()))
        print("")
        quit()
    print("Control-C to quit")
    process_audio = ProcessAudio()
    process_audio.start()
    while True:
        time.sleep(.1)
