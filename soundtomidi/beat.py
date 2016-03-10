"""Beat. Container for all things having to do with the beat of a song.

Options:
  --inifile=FILE                Name of options settings file.
                                [default: soundtomidi.ini]

"""
from __future__ import print_function
from __future__ import division
from docopt import docopt
import configparser
import os.path
import numpy as np
from datetime import datetime as dt
from aubio import tempo

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

        if os.path.exists(self.settings['inifile']):
            os.rename(self.settings['inifile'],
                      self.settings['inifile'] + "." + dt.now().strftime("%s"))
        with open(self.settings['inifile'], 'wb') as configfile:
            config.write(configfile)


class Beat:
    """Beat object that receives frames and sends MIDI messages.

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
        self.options = options
        self.beat_object = tempo(self.options.settings['balg'],
                                 int(float(self.options.settings['framesize']) *
                                     float(self.options.settings['bframemult'])),
                                 int(float(self.options.settings['framesize']) *
                                     float(self.options.settings['bframemult']) *
                                     float(self.options.settings['bhopmult'])),
                                 int(float(self.options.settings['samplerate'])))
        self.frame_arrays = np.zeros(
            (int(float(self.options.settings['bframemult'])),
             int(float(self.options.settings['framesize']))),
            dtype=np.float32)
        self.midi_processor = None
        self.sysex_command_array = []
        for command in self.options.settings['bsysexnum'].split(' '):
            self.sysex_command_array.append(int(command, 0))
        self.control_number = False
        if self.options.settings['bcontrolnum'] != 'None':
            self.control_number = int(self.options.settings['bcontrolnum'], 0)
        self.beat_sequence = []
        for item in self.options.settings['bvaltype'].split(','):
            self.beat_sequence.append(int(item.strip()))
        if not self.beat_sequence:
            self.beat_sequence = [64]
        self.beat_sequence_position = 0
        self.frame_count = 0

    def add_frame(self, frame_array):
        self.frame_arrays[self.frame_count] = frame_array
        self.frame_count += 1
        if self.frame_count == int(self.options.settings['bframemult']):
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
