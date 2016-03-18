"""standalone_curses.py

Standalone program to demonstrate how to receive and process incoming MIDI
messages from running soundtomidi on the command line.

Usage:
  standalone_curses.py [options]

Options:
  -h --help                     Show this screen.
                                Quits after.
  --listmidiports               List MIDI ports.
                                Quits after.
  --writeinifile                Write options to ini file, as specified by
                                inifile option. If the file already present,
                                a backup is made of original.
  --inifile=FILE                Name of options settings file.
                                [default: standalone_curses.ini]
  --inport=MIDIINPORT           Name of the MIDI input port. If left as
                                default, uses first MIDI port found.
                                [default: default]
  --inchannel=OUTCHANNEL        Number of the MIDI channel to receive
                                messages on.
                                Valid numbers 1-16.
                                [default: 14]
  --sysexmanf=MANF              Manufacturer prefix code for sysex messages.
                                Int or hex values, separarated by space.
                                [default: 0x7D]
  --tcontrolnum=TCONTROLNUM     Controller number to receive BPM messages.
                                [default: 14]
  --tcontroltype=TCONTROLTYPE   How to encode the BPM values for control are
                                encoded. "minus60" means value was BPM minus
                                60.
                                EG: 0 value = 60 BPM,
                                60 value = 120 BPM,
                                127 value = 187 BPM.
                                [default: minus60]
  --tsysexnum=TSYSEXNUM         Prefix for incoming BPM sysex messages.
                                [default: 0x0B]
  --tsysextype=TSYSEXTYPE       How BPM value in sysex was encoded.
                                "minus60" adds 60 to incoming value.
                                (See --tsysexcontroltype)
                                "twobytes" assumes that incoming value is
                                BPM to the tenth (EG, 128.1), was multiplied
                                by 10 (1281), then spread across two 7 bit
                                values (0x10 0x01)
                                [default: twobytes]
  --bcontrolnum=BCONTROLNUM     Controller number to receive beat messages.
                                [default: 15]
  --bsysexnum=BSYSEXNUM         Prefix for incoming beat number sysex messages.
                                [default: 0x1B]
  --rcontrolnum=FRMSNUM         Controller number to receive RMS messages.
                                [default: 20]
  --rsysexnum=FSYSEXNUM         Prefix to for incoming RMS values.
                                [default: 0x1F]
  --fsysexnum=FSYSEXNUM         Prefix for incoming frequency strength
                                sysex values.
                                [default: 0x0F]
  --pnoteon=PNOTEON             Handle note on messages for audio pitch.
                                [default: True]
  --pnoteoff=PNOTEOFF           Handle note off messages for audio pitch.
                                [default: True]
  --pcontrolnum=PCONTROLNUM     Controller number to receive pitches.
                                [default: None]
  --psysexnum=PSYSEXNUM         Prefix for incoming pitch sysex messages.
                                [default: None]

"""

from __future__ import print_function
from __future__ import division
from docopt import docopt
import configparser
import os.path
from datetime import datetime as dt
import mido
import curses


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
        self.settings = docopt(__doc__, version='Standalone Curses Demo 0.1')
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
        config.add_section('settings')
        config.set('settings', 'inport', self.settings['inport'])
        config.set('settings', 'inchannel', self.settings['inchannel'])
        config.set('settings', 'sysexmanf', self.settings['sysexmanf'])
        config.set('settings', 'tcontrolnum', self.settings['tcontrolnum'])
        config.set('settings', 'tcontroltype', self.settings['tcontroltype'])
        config.set('settings', 'tsysexnum', self.settings['tsysexnum'])
        config.set('settings', 'tsysextype', self.settings['tsysextype'])
        config.set('settings', 'bcontrolnum', self.settings['bcontrolnum'])
        config.set('settings', 'bsysexnum', self.settings['bsysexnum'])
        config.set('settings', 'rcontrolnum', self.settings['rcontrolnum'])
        config.set('settings', 'rsysexnum', self.settings['rsysexnum'])
        config.set('settings', 'fsysexnum', self.settings['fsysexnum'])
        config.set('settings', 'pnoteon', self.settings['pnoteon'])
        config.set('settings', 'pnoteoff', self.settings['pnoteoff'])
        config.set('settings', 'pcontrolnum', self.settings['pcontrolnum'])
        config.set('settings', 'psysexnum', self.settings['psysexnum'])

        if os.path.exists(self.settings['inifile']):
            os.rename(self.settings['inifile'],
                      self.settings['inifile'] + "." + dt.now().strftime("%s"))
        with open(self.settings['inifile'], 'wb') as configfile:
            config.write(configfile)


class BPM:
    def __init__(self):
        self.control_window = curses.newwin(3, 20, 0, 59)
        self.control_window.addstr(0, 0, "BPM (control msg)".center(20))
        self.sysex_window = curses.newwin(3, 20, 5, 59)
        self.sysex_window.addstr(0, 0, "BPM (sysex msg)".center(20))

        self.control_bpm = 0
        self.sysex_bpm = 0.0

    def set_control_bpm(self, bpm):
        self.control_bpm = bpm + 60
        self.control_window.addstr(1, 0, str(self.control_bpm).center(20))

    def set_sysex_bpm_two_bytes(self, two_byte_array):
        self.sysex_bpm = round(
            ((two_byte_array[0] * 128) + two_byte_array[1]) / 10.0, 1)
        self.control_window.addstr(1, 0, str(self.sysex_bpm).center(20))


class Beat:
    def __init__(self):
        self.control_window = curses.newwin(3, 50, 10, 38)
        self.control_window.addstr(0, 0, "Beat (control msg)".center(50))
        self.sysex_window = curses.newwin(3, 50, 14, 38)
        self.sysex_window.addstr(0, 0, "Beat (sysex msg)".center(50))

        self.control_beat_location = 0
        self.sysex_beat_location = 0

    def set_control_beat(self, beat_location):
        self.control_beat_location = beat_location
        self.control_window.addstr(1, 0,
                                   str(self.control_beat_location).center(50))

    def set_sysex_beat(self, beat_location_array):
        self.sysex_beat_location = beat_location_array[0]
        self.sysex_window.addstr(1, 0,
                                 str(self.sysex_beat_location).center(50))


class RMS:
    def __init__(self):
        self.control_window = curses.newwin(3, 20, 0, 38)
        self.control_window.addstr(0, 0, "RMS (control msg)".center(20))
        self.sysex_window = curses.newwin(3, 20, 5, 38)
        self.sysex_window.addstr(0, 0, "RMS (sysex msg)".center(20))
        self.control_rms = 0
        self.sysex_rms = 0

    def set_control_rms(self, rms):
        self.control_rms = rms
        self.control_window.addstr(1, 0, str(self.control_rms).center(20))

    def set_sysex_rms(self, rms_array):
        self.sysex_rms = rms_array[0]
        self.sysex_window.addstr(1, 0, str(self.sysex_rms).center(20))


class Frequencies:
    def __init__(self):
        self.sysex_window = curses.newwin(9, 37, 0, 0)
        self.sysex_window.addstr(0, 0, "Frequencies (sysex msg)".center(37))
        self.segments = 127.0 / 8.0
        self.frequencies = []

    def set_sysex_frequencies(self, frequency_array):
        self.frequencies = frequency_array
        column = (37 - len(self.frequencies)) / 2
        for value in self.frequencies:
            for x in range(8):
                if value >= self.segments * x:
                    self.sysex_window.addstr(8 - x, column, "*")
                else:
                    self.sysex_window.addstr(8 - x, column, " ")
            column += 1


class Pitch:
    def __init__(self):
        self.note_window = curses.newwin(12, 11, 10, 0)
        self.note_window.addstr(0, 0, "Pitch (n)".center(11))
        self.control_window = curses.newwin(12, 11, 10, 13)
        self.control_window.addstr(0, 0, "Pitch (c)".center(11))
        self.sysex_window = curses.newwin(12, 11, 10, 26)
        self.sysex_window.addstr(0, 0, "Pitch (s)".center(11))
        #self.margin_window1 = curses.newwin(12, 2, 10, 11)
        #self.margin_window1.addstr(1, 0, "B ")
        #self.margin_window1.addstr(2, 0, "A#")
        #self.margin_window1.addstr(3, 0, "A ")
        #self.margin_window1.addstr(4, 0, "G#")
        #self.margin_window1.addstr(5, 0, "G ")
        #self.margin_window1.addstr(6, 0, "F#")
        #self.margin_window1.addstr(7, 0, "F ")
        #self.margin_window1.addstr(8, 0, "E ")
        #self.margin_window1.addstr(9, 0, "D#")
        #self.margin_window1.addstr(10, 0, "D ")
        #self.margin_window1.addstr(11, 0, "C#")
        #self.margin_window1.addstr(12, 0, "C ")
        #self.margin_window2 = curses.newwin(13, 2, 10, 24)
        #self.margin_window2.addstr(1, 0, "B ")
        #self.margin_window2.addstr(2, 0, "A#")
        #self.margin_window2.addstr(3, 0, "A ")
        #self.margin_window2.addstr(4, 0, "G#")
        #self.margin_window2.addstr(5, 0, "G ")
        #self.margin_window2.addstr(6, 0, "F#")
        #self.margin_window2.addstr(7, 0, "F ")
        #self.margin_window2.addstr(8, 0, "E ")
        #self.margin_window2.addstr(9, 0, "D#")
        #self.margin_window2.addstr(10, 0, "D ")
        #self.margin_window2.addstr(11, 0, "C#")
        #self.margin_window2.addstr(12, 0, "C ")
        self.pitch_note = 0
        self.last_pitch_note = 0
        self.pitch_control = 0
        self.last_pitch_control = 0
        self.pitch_sysex = 0
        self.last_pitch_sysex = 0

    def set_note_pitch(self, pitch):
        self.pitch_note = pitch
        pitch_note_octave = int(self.pitch_note / 12)
        pitch_note_note = self.pitch_note - (12 * pitch_note_octave)
        self.note_window.addstr(13 - pitch_note_note, pitch_note_octave, "*")

    def set_last_note_pitch(self, last_pitch):
        self.last_pitch_note = last_pitch
        pitch_note_octave = int(self.last_pitch_note / 12)
        pitch_note_note = self.last_pitch_note - (12 * pitch_note_octave)
        self.note_window.addstr(13 - pitch_note_note, pitch_note_octave, "-")

    def set_control_pitch(self, pitch):
        self.last_pitch_control = self.pitch_control
        self.pitch_control = pitch
        pitch_control_octave = int(self.pitch_control / 12)
        pitch_control_note = self.pitch_control - (12 * pitch_control_octave)
        self.note_window.addstr(13 - pitch_control_note, pitch_control_octave,
                                "*")
        last_pitch_control_octave = int(self.last_pitch_control / 12)
        last_pitch_control_note = self.last_pitch_control - (
        12 * last_pitch_control_octave)
        self.note_window.addstr(13 - last_pitch_control_note,
                                last_pitch_control_octave, "*")

    def set_sysex_pitch(self, pitch_array):
        self.last_pitch_sysex = self.pitch_sysex
        self.pitch_sysex = pitch_array[0]
        pitch_sysex_octave = int(self.pitch_sysex / 12)
        pitch_sysex_note = self.pitch_sysex - (12 * pitch_sysex_octave)
        self.note_window.addstr(13 - pitch_sysex_note, pitch_sysex_octave, "*")
        last_pitch_sysex_octave = int(self.last_pitch_sysex / 12)
        last_pitch_sysex_note = self.last_pitch_sysex - (
            12 * last_pitch_sysex_octave)
        self.note_window.addstr(13 - last_pitch_sysex_note,
                                last_pitch_sysex_octave, "*")


class MidiReceiver:
    def __init__(self, options):
        self.midi_inport = None
        if options.settings['inport'] == 'default':
            # Get first inputname
            available_ports = mido.get_output_names()
            if available_ports:
                options.settings['inport'] = available_ports[0]
            else:
                print("No input name passed in, none found, turning midi off")
                options.settings['inport'] = ""

        self.sysex_prefix = []
        for manf_byte in options.settings['sysexmanf'].split(' '):
            self.sysex_prefix.append(int(manf_byte, 0))
        for channel in options.settings['inchannel'].split(' '):
            self.sysex_prefix.append(int(channel, 0) - 1)
        self.channel = int(options.settings['inchannel']) - 1

        try:
            self.bcontrolnum = int(options.settings['bcontrolnum'], 0)
        except ValueError:
            self.bcontrolnum = -1
        try:
            self.tcontrolnum = int(options.settings['tcontrolnum'], 0)
        except ValueError:
            self.tcontrolnum = -1
        try:
            self.rcontrolnum = int(options.settings['rcontrolnum'], 0)
        except ValueError:
            self.rcontrolnum = -1
        try:
            self.pcontrolnum = int(options.settings['pcontrolnum'], 0)
        except ValueError:
            self.pcontrolnum = -1

        try:
            self.bsysexnum = int(options.settings['bsysexnum'])
        except ValueError:
            self.bsysexnum = -1
        try:
            self.tsysexnum = int(options.settings['tsysexnum'])
        except ValueError:
            self.tsysexnum = -1
        try:
            self.rsysexnum = int(options.settings['rsysexnum'])
        except ValueError:
            self.rsysexnum = -1
        try:
            self.fsysexnum = int(options.settings['fsysexnum'])
        except ValueError:
            self.fsysexnum = -1
        try:
            self.psysexnum = int(options.settings['psysexnum'])
        except ValueError:
            self.psysexnum = -1

        self.bpm = BPM()
        self.beat = Beat()
        self.rms = RMS()
        self.frequencies = Frequencies()
        self.pitch = Pitch()

    def start(self):
        print ("Started MIDI Receiver")
        if self.midi_inport:
            with mido.open_input(self.midi_inport) as input:
                for message in input:
                    if message.type == 'control_change':
                        if message.channel == self.channel:
                            if message.control == self.bcontrolnum:
                                self.beat.set_control_beat(message.value)
                            elif message.control == self.tcontrolnum:
                                self.bpm.set_control_bpm(message.value)
                            elif message.control == self.rcontrolnum:
                                self.rms.set_control_rms(message.value)
                            elif message.control == self.pcontrolnum:
                                self.pitch.set_control_pitch(message.value)
                    elif message.type == 'sysex':
                        prefix = list(message.data[0:len(self.sysex_prefix)])
                        command = list(message.data[len(self.sysex_prefix):len(
                            self.sysex_prefix) + 1])
                        data = list(message.data[len(self.sysex_prefix) + 1:])
                        if cmp(prefix, self.sysex_prefix) == 0:
                            if command[0] == self.bsysexnum:
                                self.beat.set_sysex_beat(data)
                            elif command[0] == self.tsysexnum:
                                self.bpm.set_sysex_bpm_two_bytes(data)
                            elif command[0] == self.rsysexnum:
                                self.rms.set_sysex_rms(data)
                            elif command[0] == self.fsysexnum:
                                self.frequencies.set_sysex_frequencies(data)
                            elif command[0] == self.psysexnum:
                                self.pitch.set_sysex_pitch(data)
                    elif message.channel == self.channel:
                        if message.type == 'note_on':
                            self.pitch.set_note_pitch(message.note)
                        elif message.type == 'note_off':
                            self.pitch.set_last_pitch_note(message.note)


def main():
    main_options = Options()
    if main_options.settings['writeinifile']:
        main_options.write_options_ini()
        quit()
    elif main_options.settings['listmidiports']:
        print("\nAvailable MIDI ports:")
        print("\n".join(mido.get_output_names()))
        print("")
        quit()
    #screen.clear()
    midi_receiver = MidiReceiver(main_options)
    #screen.refresh()

    midi_receiver.start()


if __name__ == '__main__':
    # Startup. Wrapper for curse so we can control-C out of this.
    #
    # Loads the options class, and if it was one the special cases like
    # writing the inifile or printing out the midi and sound device
    # information, do that then quit.
    #
    # Otherwise, start the ProcessAudio class and get out of the way.
    #curses.wrapper(main)
    main()
