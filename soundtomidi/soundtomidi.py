"""Audio Processor. Takes live audio and generates MIDI information from it.

Here are the configuration options, and they go on and on. Some of
them are optimistic that I'll come back later and add other options, but
don't count on it.  Probably the most important thing to wrap your head
around is that you set a frame size for audio capture (say, 512), and each
audio processor uses stores some multiple of that before it does anything.
A multiple of "4" means the audio processor waits until 2048 bytes (4x512)
have arrived before doing anything. The hop size (which aubio uses as a
window for its work) is then a multiple of that.  Most of the time it seems
like the hop size should be exactly half of the window size, so you'd put
.5 in that configuration option.  If the window size and hop size should be
the same (which worked best for me for beat detection), enter 1 as the
configuration option.

On the MIDI side, nearly everything is about what controller, note, or sysex
message should be used to output information. Presumably you'll just need
one or the other for each audio processor. It really depends on what is going
to be on the receiving end of this information how you set this up. The
defaults use some safe options--manufacturer is the MIDI "for educational use"
prefix, and the controllers are not officially mapped to anything. Notes are
only (potentially) used for pitches, but it should be clear how you could
modify the code to use notes for anything else as well.

Usage:
  audioprocessor.py [options]

Options:
  -h --help                     Show this screen.
                                Quits after.
  --listsounddevices            List available sound devices.
                                Quits after.
  --listmidiports               List MIDI ports.
                                Quits after.
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
  --stdout=STDOUT               Echo message to standard out.
                                [default: False]
  --stdoutformat=STDOUTFORMAT   Format for standard out messages. Options are
                                "verbose", "bytes", "bin" or "hex".
                                [default: verbose]
  --midiout=MIDIOUT             Send MIDI messages?
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
  --gettempo=TEMPO              Get the tempo of the audio.
                                [default: True]
  --talg=TALG                   Aubio algorithm for determining the tempo.
                                [default: default]
  --tframemult=TFRAMEMULT       Number of frames to use in calculation.
                                [default: 1]
  --thopmult=THOPMULT           Hop size, as percent of FRAMEMULT.
                                [default: .5]
  --taverage=TAVERAGE           Number of BPM values to average.
                                [default: 1]
  --tcount=TCOUNT               Number of BPM averages to be stored before
                                the most common one is sent as a message.
                                [default: 1]
  --tcontrolnum=TCONTROLNUM     Controller number to send BPM messages.
                                If "None", no control messages will be sent.
                                [default: 14]
  --tcontroltype=TCONTROLTYPE   How to encode the BPM value for control.
                                "minus60" sends BPM value minus 60.
                                EG: 60 BPM = 0 value,
                                120 BPM = 60 value,
                                187 BPM = 127 value.
                                [default: minus60]
  --tsysexnum=TSYSEXNUM         Prefix to send prior to BPM in
                                sysex messages.
                                If "None", no sysex messages will be sent.
                                [default: 0x0B]
  --tsysextype=TSYSEXTYPE       How to encode the BPM value for sysex.
                                "minus60" sends BPM value minus 60.
                                (See --tsysexcontroltype)
                                "twobytes" takes the BPM value to
                                the tenth (EG, 128.1), multiplies it
                                by 10 (1281), then spreads this
                                across two 7 bit values (0x10 0x01)
                                [default: twobytes]
  --getbeats=BEATS              Get the beats of the audio.
                                [default: True]
  --balg=BALG                   Aubio algorithm to use for the beat.
                                [default: default]
  --bframemult=BFRAMEMULT       Number of frames to use in calculation.
                                [default: 1]
  --bhopmult=BHOPMULT           Hop size, as percent of FRAMEMULT.
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
  --rframemult=FFRAMEMULT       Number of frames to use in calculation.
                                [default: 4]
  --rhopmult=FHOPMULT           Hop size, as percent of FRAMEMULT.
                                [default: 1]
  --rcontrolnum=FRMSNUM         Controller number to send RMS messages.
                                If "None", no frequency strength sysex messages
                                will be sent.
                                [default: 20]
  --rsysexnum=FSYSEXNUM         Prefix to send prior to RMS values
                                If "None", no RMS sysex messages will be sent.
                                [default: 0x1F]
  --rgraceful=FRMSGRACEFUL      Gracefully let go of RMS peaks.
                                EG: one frame peaks at 100, followed by a drop
                                to 20. Instead of immediately reflecting the
                                new value, this rule sets a cut-off for the
                                drop to the chosen percent. The higher the
                                percent, the slower the decline. New high peaks
                                reset this graceful fade and it starts again.
                                Set to 0.0 to turn off.
                                [default: .5]
  --getfrequencies=FREQS        Get the strength of filtered frequencies.
                                [default: True]
  --falg=FALG                   Aubio algorithm to use for determining
                                the strength of the frequencies.
                                [default: default]
  --fframemult=FFRAMEMULT       Number of frames to use in calculation.
                                [default: 4]
  --fhopmult=FHOPMULT           Hop size, as percent of FRAMEMULT.
                                [default: 1]
  --fcount=FCOUNT               Number of frequency values to hold
                                before taking any action. Maximum value
                                of set will be sent.
                                [default: 2]
  --fbuckets=FBUCKETS           Filter bands to use for use for dividing up
                                frequencies. Comma separated list of values
                                plus a low and high end barrier value.
                                See Aubio docs "filterbanks" for more details.
                                Shortcuts "octave" and "third-octave" shortcut
                                for standard octave or 1/3 octave bands.
                                [default: third-octave]
  --fsysexnum=FSYSEXNUM         Prefix to send prior to frequency strength
                                values.
                                If "None", no sysex messages will be sent.
                                [default: 0x0F]
  --fgraceful=FGRACEFUL         Gracefully let go of frequency peaks.
                                EG: a frame peaks at 100, followed by
                                a drop to 20. Instead of immediately reflecting
                                the new value, this rule sets a cut-off for the
                                drop to the chosen percent. The higher the
                                percent, the slower the decline. New high peaks
                                reset this graceful fade and it starts again.
                                Set to 0.0 to turn off.
                                [default: .8]
  --getpitch=PITCHES            Get the fundamental pitch of the audio.
                                [default: True]
  --palg=PALG                   Aubio algorithm to use for pitch of the audio.
                                [default: yin]
  --pframemult=PFRAMEMULT       Number of frames to use in calculation.
                                [default: 2]
  --phopmult=PHOPMULT           Hop size, as percent of FRAMEMULT.
                                [default: .5]
  --ptolerance=PTOLERANCE       Required confidence level for a pitch.
                                [default: 0.5]
  --pcount=PCOUNT               Number of pitch averages to be stored before
                                the most common one is sent as a message.
                                [default: 8]
  --plowcutoff=PLOWCUTOFF       Lowest pitch to consider.
                                [default: 0]
  --phighcutoff=PHIGHCUTOFF     Highest pitch to consider.
                                [default: 127]
  --pfoldoctaves=PFOLDOCTAVES   Return just 12 note values instead of the
                                possible 128.
                                [default: False]
  --pnumoffset=PNUMOFFSET       Used only with the above option. Shifts the "C"
                                value to somewhere else, and each note above
                                that. Middle C is "60", which is the default.
                                [default: 60]
  --pnoteon=PNOTEON             Send note on messages for the audio pitch.
                                [default: True]
  --pnoteoff=PNOTEOFF           Send note off messages when a new audio
                                pitch doesn't match previous pitch.
                                [default: True]
  --pcontrolnum=PCONTROLNUM     Controller number to send pitches.
                                If "None", no control messages will be sent.
                                [default: 21]
  --psysexnum=PSYSEXNUM         Prefix to send prior to sending note value.
                                If "None", no sysex messages will be sent.
                                [default: 0x0C]

"""
from __future__ import print_function
from __future__ import division
from docopt import docopt
import configparser
import os.path
import sys
import time
import numpy as np
import sounddevice as sd
from datetime import datetime as dt
from collections import Counter
from aubio import pitch, tempo, pvoc, filterbank, fvec
import mido
import math


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
        self.settings = docopt(__doc__, version='Audio Processor 0.1')
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
        config.add_section('stdout')
        config.set('stdout', 'stdout', self.settings['stdout'])
        config.set('stdout', 'stdoutformat', self.settings['stdoutformat'])
        config.add_section('midi')
        config.set('midi', 'midiout', self.settings['midiout'])
        config.set('midi', 'outport', self.settings['outport'])
        config.set('midi', 'outchannel', self.settings['outchannel'])
        config.set('midi', 'sysexmanf', self.settings['sysexmanf'])
        config.add_section('tempo')
        config.set('tempo', 'gettempo', self.settings['gettempo'])
        config.set('tempo', 'talg', self.settings['talg'])
        config.set('tempo', 'tframemult', self.settings['tframemult'])
        config.set('tempo', 'thopmult', self.settings['thopmult'])
        config.set('tempo', 'taverage', self.settings['taverage'])
        config.set('tempo', 'tcount', self.settings['tcount'])
        config.set('tempo', 'tcontrolnum', self.settings['tcontrolnum'])
        config.set('tempo', 'tcontroltype', self.settings['tcontroltype'])
        config.set('tempo', 'tsysexnum', self.settings['tsysexnum'])
        config.set('tempo', 'tsysextype', self.settings['tsysextype'])
        config.add_section('beats')
        config.set('beats', 'getbeats', self.settings['getbeats'])
        config.set('beats', 'balg', self.settings['balg'])
        config.set('beats', 'bframemult', self.settings['bframemult'])
        config.set('beats', 'bhopmult', self.settings['bhopmult'])
        config.set('beats', 'bcontrolnum', self.settings['bcontrolnum'])
        config.set('beats', 'bsysexnum', self.settings['bsysexnum'])
        config.set('beats', 'bvaltype', self.settings['bvaltype'])
        config.set('beats', 'bclock', self.settings['bclock'])
        config.add_section('rms')
        config.set('rms', 'getrms', self.settings['getrms'])
        config.set('rms', 'rframemult', self.settings['rframemult'])
        config.set('rms', 'rhopmult', self.settings['rhopmult'])
        config.set('rms', 'rcontrolnum', self.settings['rcontrolnum'])
        config.set('rms', 'rsysexnum', self.settings['rsysexnum'])
        config.set('rms', 'rgraceful', self.settings['rgraceful'])
        config.add_section('frequencies')
        config.set('frequencies', 'getfrequencies',
                   self.settings['getfrequencies'])
        config.set('frequencies', 'falg', self.settings['falg'])
        config.set('frequencies', 'fframemult', self.settings['fframemult'])
        config.set('frequencies', 'fhopmult', self.settings['fhopmult'])
        config.set('frequencies', 'fcount', self.settings['fcount'])
        config.set('frequencies', 'fbuckets', self.settings['fbuckets'])
        config.set('frequencies', 'fsysexnum', self.settings['fsysexnum'])
        config.set('frequencies', 'fgraceful', self.settings['fgraceful'])
        config.add_section('pitch')
        config.set('pitch', 'getpitch', self.settings['getpitch'])
        config.set('pitch', 'palg', self.settings['palg'])
        config.set('pitch', 'pframemult', self.settings['pframemult'])
        config.set('pitch', 'phopmult', self.settings['phopmult'])
        config.set('pitch', 'ptolerance', self.settings['ptolerance'])
        config.set('pitch', 'pcount', self.settings['pcount'])
        config.set('pitch', 'plowcutoff', self.settings['plowcutoff'])
        config.set('pitch', 'phighcutoff', self.settings['phighcutoff'])
        config.set('pitch', 'pfoldoctaves', self.settings['pfoldoctaves'])
        config.set('pitch', 'pnumoffset', self.settings['pnumoffset'])
        config.set('pitch', 'pnoteon', self.settings['pnoteon'])
        config.set('pitch', 'pnoteoff', self.settings['pnoteoff'])
        config.set('pitch', 'pcontrolnum', self.settings['pcontrolnum'])
        config.set('pitch', 'psysexnum', self.settings['psysexnum'])

        if os.path.exists(self.settings['inifile']):
            os.rename(self.settings['inifile'],
                      self.settings['inifile'] + "." + dt.now().strftime("%s"))
        with open(self.settings['inifile'], 'wb') as configfile:
            config.write(configfile)


class TempoFinder:
    """Tempo finder object that receives frames and sends MIDI messages.

    Sticky object that initializes with the Aubio tempo object, as adjusted
    by the many configuration options that are available. Sets up a holder
    for incoming frames of audio data.  Once there are enough frames to work
    with, the data is combined and processed by the tempo object. Results
    are cleaned up, and MIDI messages as configured are sent out.

    There appear to be many ways of trying to send this information via MIDI.
    The issue is that MIDI data bytes are 0-127. Two options are built in.
    One, just subtract 60 from the rounded BPM value and use that. On the
    receiving end, just add 60 back to the value and there you go. Another
    option is to spread the number out across two 7 bit bytes (that sounds
    wrong), which is the default for sysex messages. The BPM is multiplied
    by 10, rounded, then bit shifted across two bytes. On the receiving end,
    reassemble to value like this:

    (first_data_byte*128)+second_data_byte) / 10.0

    """

    def __init__(self, options):
        self.tempo_object = tempo(options.settings['talg'],
                                  int(float(options.settings['framesize']) *
                                      float(options.settings['tframemult'])),
                                  int(float(options.settings['framesize']) *
                                      float(options.settings['tframemult']) *
                                      float(options.settings['thopmult'])),
                                  int(float(options.settings['samplerate'])))
        self.frame_arrays = np.zeros(
            (int(float(options.settings['tframemult'])),
             int(float(options.settings['framesize']))),
            dtype=np.float32)
        self.midi_processor = None
        self.sysex_command_array = []
        for command in options.settings['tsysexnum'].split(' '):
            self.sysex_command_array.append(int(command, 0))
        self.bpm_sysex_rule = self.bpm_to_two_bytes
        if options.settings['tsysextype'] == 'twobytes':
            self.bpm_sysex_rule = self.bpm_to_two_bytes
        elif options.settings['tsysextype'] == 'minus60':
            self.bpm_sysex_rule = self.bpm_minus_sixty
        self.control_number = False
        if options.settings['tcontrolnum'] != 'None':
            self.control_number = int(options.settings['tcontrolnum'], 0)
        self.bpm_control_rule = self.bpm_minus_sixty
        if options.settings['tcontroltype'] == 'minus60':
            self.bpm_control_rule = self.bpm_minus_sixty
        self.frame_count = 0
        self.BPMs = []
        self.average_BPMs = []
        self.last_BPM = 0.0
        self.average = int(options.settings['taverage'])
        self.count = int(options.settings['tcount'])
        self.frame_multiplier = int(options.settings['tframemult'])

    def add_frame(self, frame_array):
        self.frame_arrays[self.frame_count] = frame_array
        self.frame_count += 1
        if self.frame_count == self.frame_multiplier:
            combined_array = np.ravel(self.frame_arrays)
            self.tempo_object(combined_array)
            bpm = self.tempo_object.get_bpm()
            if bpm < 60.0:
                bpm *= 2.0
                if bpm < 60.0:
                    bpm = 60.0
            if bpm > 187.0:
                bpm /= 2.0
                if bpm > 187.0:
                    bpm = 187.0
            self.BPMs.append(bpm)
            if len(self.BPMs) > self.average:
                del self.BPMs[0]
            self.average_BPMs.append(round(sum(self.BPMs) /
                                           len(self.BPMs), 1))
            if len(self.average_BPMs) > self.count:
                del self.average_BPMs[0]
            most_bpm, foo = Counter(self.average_BPMs).most_common(1)[0]
            if most_bpm != self.last_BPM:
                self.last_BPM = most_bpm
                if self.control_number:
                    self.midi_processor.add_control_message(
                        self.control_number, self.bpm_control_rule(most_bpm)[0]
                    )
                if self.sysex_command_array:
                    self.midi_processor.add_sysex_message(
                        self.sysex_command_array,
                        self.bpm_sysex_rule(most_bpm)
                    )
            self.frame_count = 0

    @staticmethod
    def bpm_to_two_bytes(bpm):
        bpm = int(bpm * 10)
        bytesarray = [bpm >> 7, bpm & 0x7F]
        return bytesarray

    @staticmethod
    def bpm_minus_sixty(bpm):
        bpm = int(bpm - 60)
        if bpm < 0:
            bpm = 0
        elif bpm > 127:
            bpm = 127
        return [bpm]


class BeatFinder:
    """Beat finder object that receives frames and sends MIDI messages.

    Sticky object that initializes with the Aubio tempo object, as adjusted
    by the many configuration options that are available. Sets up a holder
    for incoming frames of audio data.  Once there are enough frames to work
    with, the data is combined and processed by the tempo object. Results
    are cleaned up, and MIDI messages as configured are sent out.

    TODO: Add a mechanism for sending 24 clock tick messages. Trivial to
    just send 24 messages to the MidiProcessor right away after a beat,
    but the clock ticks should probably be at spaced out evenly.  The problem
    comes in when the music speeds up and the next beat arrives before the 24
    clock ticks have sent. It also really saturates the MidiProcessor, as well
    as software that is listening to the messages.  Leaving this out for now.

    """

    def __init__(self, options):
        self.beat_object = tempo(options.settings['balg'],
                                 int(float(options.settings['framesize']) *
                                     float(options.settings['bframemult'])),
                                 int(float(options.settings['framesize']) *
                                     float(options.settings['bframemult']) *
                                     float(options.settings['bhopmult'])),
                                 int(float(options.settings['samplerate'])))
        self.frame_arrays = np.zeros(
            (int(float(options.settings['bframemult'])),
             int(float(options.settings['framesize']))),
            dtype=np.float32)
        self.midi_processor = None
        self.sysex_command_array = []
        for command in options.settings['bsysexnum'].split(' '):
            self.sysex_command_array.append(int(command, 0))
        self.control_number = False
        if options.settings['bcontrolnum'] != 'None':
            self.control_number = int(options.settings['bcontrolnum'], 0)
        self.beat_sequence = []
        for item in options.settings['bvaltype'].split(','):
            self.beat_sequence.append(int(item.strip()))
        if not self.beat_sequence:
            self.beat_sequence = [64]
        self.beat_sequence_position = 0
        self.frame_count = 0
        self.frame_multiplier = int(options.settings['bframemult'])

    def add_frame(self, frame_array):
        self.frame_arrays[self.frame_count] = frame_array
        self.frame_count += 1
        if self.frame_count == self.frame_multiplier:
            combined_array = np.ravel(self.frame_arrays)
            is_beat = self.beat_object(combined_array)
            if is_beat:
                value_data = [self.beat_sequence[self.beat_sequence_position]]
                if self.control_number:
                    self.midi_processor.add_control_message(
                        self.control_number, self.beat_sequence_position
                    )
                if self.sysex_command_array:
                    self.midi_processor.add_sysex_message(
                        self.sysex_command_array, value_data
                    )
                self.beat_sequence_position += 1
                if self.beat_sequence_position == len(self.beat_sequence):
                    self.beat_sequence_position = 0
            self.frame_count = 0


class RMSFinder:
    """RMS finder object that receives frames and sends MIDI messages.

    Sticky object that sets up a holder for incoming frames of audio data.
    Once there are enough frames to work with, the data is combined and
    processed by the filter object. Results are cleaned up, and MIDI messages
    as configured are sent out.

    This function does not rely on the Aubio library.

    """

    def __init__(self, options):
        self.midi_processor = None
        self.sysex_rms_command_array = []
        for command in options.settings['rsysexnum'].split(' '):
            self.sysex_rms_command_array.append(int(command, 0))
        self.rms_control_number = False
        if options.settings['rcontrolnum'] != 'None':
            self.rms_control_number = \
                int(options.settings['rcontrolnum'], 0)
        self.frame_arrays = np.zeros(
            (int(float(options.settings['rframemult'])),
             int(float(options.settings['framesize']))),
            dtype=np.float32)
        self.frame_count = 0
        self.max_rms = 0
        self.last_scaled_rms = 0
        self.frame_multiplier = int(options.settings['rframemult'])
        self.graceful = float(options.settings['rgraceful'])

    def add_frame(self, frame_array):
        self.frame_arrays[self.frame_count] = frame_array
        self.frame_count += 1
        if self.frame_count == self.frame_multiplier:
            self.frame_count = 0
            combined_array = np.ravel(self.frame_arrays)
            rms = self.qmean(combined_array)
            if rms > self.max_rms:
                self.max_rms = rms
            if self.max_rms > 0:
                scaled_rms = int(127 * (rms / self.max_rms))
                if scaled_rms != self.last_scaled_rms:
                    graceful_rms = int(self.last_scaled_rms * self.graceful)
                    if scaled_rms < graceful_rms:
                        scaled_rms = graceful_rms
                    if self.rms_control_number:
                        self.midi_processor.add_control_message(
                            self.rms_control_number, scaled_rms)
                    if self.sysex_rms_command_array:
                        self.midi_processor.add_sysex_message(
                            self.sysex_rms_command_array, [scaled_rms])
                    self.last_scaled_rms = scaled_rms

    @staticmethod
    def qmean(num):
        return math.sqrt(sum(n * n for n in num) / len(num))


class FrequenciesFinder:
    """Frequency finder object that receives frames and sends MIDI messages.

    Sticky object that initializes with the Aubio filter object, as adjusted
    by the many configuration options that are available. Sets up a holder
    for incoming frames of audio data.  Once there are enough frames to work
    with, the data is combined and processed by the filter object. Results
    are cleaned up, and MIDI messages as configured are sent out.

    Note that this is definitely the most challenging processing work, and
    there is potential memory leak issue as described below.

    """

    def __init__(self, options):
        if options.settings['fbuckets'] == 'third-octave':
            options.settings['fbuckets'] = [22.4,
                                            25, 31.5, 40, 50, 63,
                                            80, 100, 125, 160, 200,
                                            250, 315, 400, 500, 630,
                                            800, 1000, 1250, 1600, 2000,
                                            2500, 3150, 4000, 5000, 6300,
                                            8000, 10000, 12500, 16000, 20000,
                                            22390]
        elif options.settings['fbuckets'] == 'octave':
            options.settings['fbuckets'] = [22,
                                            31.5, 63, 125, 250, 500,
                                            1000, 2000, 4000, 8000, 16000,
                                            22720]
        self.midi_processor = None
        self.sysex_command_array = []
        for command in options.settings['fsysexnum'].split(' '):
            self.sysex_command_array.append(int(command, 0))
        self.filter_bank = filterbank(len(options.settings['fbuckets']) - 2,
                                      (int(options.settings['framesize']) *
                                       int(options.settings['fframemult'])))
        self.frequencies = fvec(options.settings['fbuckets'])
        self.filter_bank.set_triangle_bands(self.frequencies,
                                            int(options.settings[
                                                    'samplerate']))
        self.phase_vocoder = pvoc(int(float(options.settings['framesize']) *
                                      float(options.settings['fframemult'])),
                                  int(float(options.settings['framesize']) *
                                      float(options.settings['fframemult']) *
                                      float(options.settings['fhopmult'])))

        self.frame_arrays = np.zeros(
            (int(float(options.settings['fframemult'])),
             int(float(options.settings['framesize']))),
            dtype=np.float32)
        self.frame_count = 0
        self.maximum_frequencies = np.zeros(
            (len(options.settings['fbuckets']) - 2,), dtype=np.float32)
        self.last_energies = np.zeros((len(options.settings['fbuckets']) - 2,),
                                      dtype=np.float32)
        self.count_energies = np.zeros((int(options.settings['fcount']),
                                        (len(options.settings[
                                                 'fbuckets']) - 2)),
                                       dtype=np.float32)
        self.energy_count = 0
        self.rest_stop = 0
        self.frame_multiplier = int(options.settings['fframemult'])
        self.count = int(options.settings['fcount'])
        self.graceful = float(options.settings['fgraceful'])

    def add_frame(self, frame_array):
        self.frame_arrays[self.frame_count] = frame_array
        self.frame_count += 1
        if self.frame_count == self.frame_multiplier:
            self.frame_count = 0
            combined_array = np.ravel(self.frame_arrays)
            # This is causing a memory leak on a OSX Brew installed version of
            # Aubio, at least according to "top". Even creating and destroying
            # the phase vocoder each time through the loop doesn't seem to
            # solve the problem. I believe the intent is for the phase vocoder
            # to hold previous runs to match up previous calls with data, but
            # it appears to be a little too sticky.
            fftgrain = self.phase_vocoder(combined_array)
            self.count_energies[self.energy_count] = self.filter_bank(fftgrain)
            self.energy_count += 1
            if self.energy_count == self.count:
                self.energy_count = 0
                energies = np.amax(self.count_energies, axis=0)
                self.maximum_frequencies = np.maximum(energies,
                                                      self.maximum_frequencies)
                energies = np.divide(energies, self.maximum_frequencies)
                energies = np.maximum(energies, self.last_energies)
                self.last_energies = energies * self.graceful
                energies *= 127.0
                int_energies = energies.astype(int)
                if self.sysex_command_array:
                    self.midi_processor.add_sysex_message(
                        self.sysex_command_array, int_energies)


class PitchFinder:
    """Pitch finder object that receives frames and sends MIDI messages.

    Sticky object that initializes with the Aubio pitch object, as adjusted
    by the many configuration options that are available. Sets up a holder
    for incoming frames of audio data.  Once there are enough frames to work
    with, the data is combined and processed by the pitch object. Results
    are cleaned up, and MIDI messages as configured are sent out.

    You can send (and probably should) both note_on and note_off messages
    here.  Note_off messages are sent when an incoming note doesn't match
    the previously sent one. The control and sysex message types on the other
    hand only send when there is new note on information.

    """

    def __init__(self, options):
        self.algorithm = options.settings['palg']
        self.frame_size = float(options.settings['framesize'])
        self.frame_multiplier = int(options.settings['pframemult'])
        self.hop_multiplier = float(options.settings['phopmult'])
        self.samplerate = float(options.settings['samplerate'])
        self.tolerance = float(options.settings['ptolerance'])
        self.sysexnumber = options.settings['psysexnum']
        self.sysex_command_array = []
        if options.settings['psysexnum'] != 'None':
            for command in options.settings['psysexnum'].split(' '):
                self.sysex_command_array.append(int(command, 0))
        self.control_number = False
        if options.settings['pcontrolnum'] != 'None':
            self.control_number = int(options.settings['pcontrolnum'], 0)
        self.send_note_ons = False
        if options.settings['pnoteon'] == 'True':
            self.send_note_ons = True
        if options.settings['pnoteoff'] == 'True':
            self.send_note_offs = True
        self.count = int(options.settings['pcount'])
        self.low_cutoff = int(options.settings['plowcutoff'])
        self.high_cutoff = int(options.settings['phighcutoff'])
        self.fold_octaves = False
        if options.settings['pfoldoctaves'] == 'True':
            self.fold_octaves = True
        self.num_offset = int(options.settings['pnumoffset'])
        self.midi_processor = None

        self.pitch_object = pitch(self.algorithm,
                                  int(self.frame_size *
                                      self.frame_multiplier),
                                  int(self.frame_size *
                                      self.frame_multiplier *
                                      self.hop_multiplier),
                                  int(self.samplerate))
        if self.tolerance != 'None':
            self.pitch_object.set_tolerance(self.tolerance)
        self.pitch_object.set_unit('midi')
        self.frame_arrays = np.zeros(
            (int(self.frame_multiplier),
             int(self.frame_size)),
            dtype=np.float32)
        self.frame_count = 0
        self.most_pitches = [-1]
        self.pitch_count = 0
        self.last_pitch = 0

    def add_frame(self, frame_array):
        self.frame_arrays[self.frame_count] = frame_array
        self.frame_count += 1
        if self.frame_count == self.frame_multiplier:
            self.frame_count = 0
            combined_array = np.ravel(self.frame_arrays)
            pitches = self.pitch_object(combined_array)
            for x in range(
                    int(round(self.pitch_object.get_confidence() * 10))):
                self.most_pitches.append(self.midify_pitch(pitches))
            self.pitch_count += 1
            if self.pitch_count == self.count:
                self.pitch_count = 0
                most_pitch, foo = Counter(self.most_pitches).most_common(1)[0]
                if most_pitch != self.last_pitch:
                    if most_pitch == -1:
                        if self.send_note_offs:
                            self.midi_processor.add_note_off_message(
                                self.last_pitch)
                    elif self.last_pitch == -1:
                        if self.send_note_ons:
                            self.midi_processor.add_note_on_message(most_pitch)
                        if self.control_number:
                            self.midi_processor.add_control_message(
                                self.control_number, most_pitch)
                        if self.sysex_command_array:
                            self.midi_processor.add_sysex_message(
                                self.sysex_command_array, [most_pitch]
                            )
                    else:
                        if self.send_note_offs:
                            self.midi_processor.add_note_off_message(
                                self.last_pitch)
                        if self.send_note_offs:
                            self.midi_processor.add_note_on_message(most_pitch)
                        if self.control_number:
                            self.midi_processor.add_control_message(
                                self.control_number, most_pitch)
                        if self.sysex_command_array:
                            self.midi_processor.add_sysex_message(
                                self.sysex_command_array, [most_pitch]
                            )
                    self.last_pitch = most_pitch
                self.most_pitches = [-1]

    def midify_pitch(self, _pitch):
        _pitch = int(round(_pitch[0]))
        if _pitch <= 0:
            _pitch = -1
        if _pitch > 127:
            _pitch = -1
        if self.low_cutoff > _pitch > self.high_cutoff:
            _pitch = -1
        if self.fold_octaves:
            if 0 <= _pitch <= 120:
                _pitch %= 12
                _pitch += self.num_offset
            else:
                _pitch = -1

        return _pitch


class MidiProcessor:
    """Wrapper class for receiving messages and sending out via mido library.

    Sticky object that receives messages from the various audio processing
    classes and MIDIfies them using the mido library.  Deals with
    the custom manufacturer sysex prefix bytes.

    """

    def __init__(self, options):
        self.midi_outport = None
        self.sysex_prefix = []
        for manf_byte in options.settings['sysexmanf'].split(' '):
            self.sysex_prefix.append(int(manf_byte, 0))
        for channel in options.settings['outchannel'].split(' '):
            self.sysex_prefix.append(int(channel, 0) - 1)
        self.channel = int(options.settings['outchannel']) - 1
        self.stdout = False
        if options.settings['stdout'] == 'True':
            self.stdout = True
            if options.settings['stdoutformat'] == 'bytes':
                self.stdoutformat = 1
            elif options.settings['stdoutformat'] == 'bin':
                self.stdoutformat = 2
            elif options.settings['stdoutformat'] == 'hex':
                self.stdoutformat = 3
            else:
                self.stdoutformat = 0

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
        if self.stdout:
            if self.stdoutformat == 0:
                print(mido_message)
            elif self.stdoutformat == 1:
                sys.stdout.write(str(mido_message.bytes()))
            elif self.stdoutformat == 2:
                sys.stdout.write(mido_message.bin())
            elif self.stdoutformat == 3:
                sys.stdout.write(mido_message.hex() + ' ')


class ProcessAudio:
    """Primary loop. Take audio frames and deliver to audio processors.

    Using sounddevice audio library, and as configured by options, take
    incoming data from sound card and send a copy of the audio data to
    the audio processors that are turned on.  Responsible for initializing
    the audio processors and midi processor.

    """

    def __init__(self, options):
        self.midi_processor = MidiProcessor(options)
        if options.settings['midiout']:
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
            self.beat_finder = BeatFinder(options)
            self.beat_finder.midi_processor = self.midi_processor
        else:
            self.beat_finder = None
        if options.settings['gettempo'] == 'True':
            self.tempo_finder = TempoFinder(options)
            self.tempo_finder.midi_processor = self.midi_processor
        else:
            self.tempo_finder = None
        if options.settings['getrms'] == 'True':
            self.rms_finder = RMSFinder(options)
            self.rms_finder.midi_processor = self.midi_processor
        else:
            self.rms_finder = None
        if options.settings['getfrequencies'] == 'True':
            self.frequencies_finder = FrequenciesFinder(options)
            self.frequencies_finder.midi_processor = self.midi_processor
        else:
            self.frequencies_finder = None
        if options.settings['getpitch'] == 'True':
            self.pitch_finder = PitchFinder(options)
            self.pitch_finder.midi_processor = self.midi_processor
        else:
            self.pitch_finder = None
        if options.settings['inputdevice'] == 'default':
            options.settings['inputdevice'] = sd.default.device['input']
        self.input_device = options.settings['inputdevice']
        self.channels = int(options.settings['channels'])
        self.blocksize = int(options.settings['framesize'])
        self.samplerate = int(options.settings['samplerate'])

    def callback(self, data, ignore_frames, ignore_time, ignore_status):
        if any(data):
            if self.beat_finder:
                self.beat_finder.add_frame(data[:, 0])
            if self.tempo_finder:
                self.tempo_finder.add_frame(data[:, 0])
            if self.rms_finder:
                self.rms_finder.add_frame(data[:, 0])
            if self.frequencies_finder:
                self.frequencies_finder.add_frame(data[:, 0])
            if self.pitch_finder:
                self.pitch_finder.add_frame(data[:, 0])

    def start(self):
        with sd.InputStream(device=self.input_device,
                            channels=self.channels,
                            callback=self.callback,
                            blocksize=self.blocksize,
                            samplerate=self.samplerate):
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
    main_options = Options()
    if main_options.settings['writeinifile']:
        main_options.write_options_ini()
        quit()
    elif main_options.settings['listsounddevices'] or main_options.settings[
        'listmidiports']:
        if main_options.settings['listsounddevices']:
            print("\nAvailable sound devices:")
            print(sd.query_devices())
        if main_options.settings['listmidiports']:
            print("\nAvailable MIDI ports:")
            print("\n".join(mido.get_output_names()))
        print("")
        quit()
    print("Control-C to quit")
    process_audio = ProcessAudio(main_options)
    process_audio.start()
    while True:
        time.sleep(.1)
