=====
Usage
=====

Command Line
============
Command line usage is pretty simple. From the command line, just run::

    python soundtomidi.py

To see what sound devices are available on your system::

    python soundtomidi.py --listsounddevices

To see what MIDI devices are available on your system::

    python soundtomidi.py --listmidiports

To modify a default parameter from the command line::

    python soundtomidi.py --stdout True --stdoutformat verbose

To write an INI file with the default parameters for easy modification::

    python soundtomidi.py --writeinifile

To use a specified INI file (values overrule defaults and command line)::

    python soundtomidi.py --inifile foo.ini


As an import
============
If you want to include this into an program directly, you'll need to populate
the options dictionary and start up ProcessAudio.  This is the bare minimum
to get it up and going.::

    from soundtomidi import soundtomidi
    options = soundtomidi.Options()
    process_audio = soundtomidi.ProcessAudio(options)
    process_audio.start()

Once ProcessAudio is started, it does not return, so you probably want to
stick it into a thread::

    import time
    import threading
    from soundtomidi import soundtomidi
    options = soundtomidi.Options()
    process_audio = soundtomidi.ProcessAudio(options)
    thread = threading.Thread(target=process_audio.start)
    thread.daemon = True
    thread.start()
    while True:
        print("Doing some other stuff")
        time.sleep(1)

