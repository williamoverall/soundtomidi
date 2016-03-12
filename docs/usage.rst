=====
Usage
=====

Command Line
============
Command line usage is pretty simple. From the command line, just run::

    python soundtomidi/main.py

To see what sound devices are available on your system::

    python soundtomidi/main.py --listsounddevices

To see what MIDI devices are available on your system::

    python soundtomidi/main.py --listmidiports

To modify a default parameter from the command line::

    python soundtomidi/main.py --stdout True --stdoutformat verbose

To write an INI file with the default parameters for easy modification::

    python soundtomidi/main.py --writeinifile

To use a specified INI file (values overrule defaults and command line)::

    python soundtomidi/main.py --inifile foo.ini


As an import
============
If you want to include this into an program directly, you'll need to populate
the options dictionary and start up ProcessAudio.  This should do it (but
untested)::

    options = Options()
    process_audio = ProcessAudio()
    process_audio.start()

