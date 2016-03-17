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
