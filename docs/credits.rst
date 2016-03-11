=======
Credits
=======

This is built using existing libraries from people a whole lot smarter than me,
of which these are particularly of note.

docopt
======
Provided some sanity with the insane amount of tweaks that one might
want to do in all of this.

sounddevice
===========
There are several very good options for dealing with incoming audio.
I can't remember exactly why I chose this one except that handily
put the data into numpy arrays for me.

aubio
=====
Wow. This is something else. This is a C (I think) library that
does all of the mathy stuff with the audio samples. It has Python
wrappers thankfully that made this possible. I barely understand any of
the terminology, and the documentation is really just looking at the
Python code examples, but it pretty much did everything I wanted it
to do. Installation was a bit of trial, and I cannot seem to get it
to build for Python 3.5 for anything. I'm also concerned about a
possibly memory leak in the phase vocoder, but there's a very good
chance it's my lack of knowledge that is causing it.

mido
====
I really like this library for dealing with MIDI messages.
Very well documented and simple to use on both the sending and
receiving end. Which means I don't have much to say about it--it works
and it works well.