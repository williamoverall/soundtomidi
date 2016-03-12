=======
Credits
=======

This is built using existing libraries from people a whole lot smarter than me,
of which these are particularly of note.

docopt
======
The `docopt <http://docopt.org>`_ package provided some sanity with the insane
amount of tweaks that one might want to do in all of this.

sounddevice
===========
The `python-sounddevice <http://python-sounddevice.readthedocs.org/en/0.3.1/>`_
package is one of several very good packages for dealing with incoming audio,
but I liked this one because it conveniently put incoming frames directly into
a numpy float32 array for me.

aubio
=====
`Aubio <http://aubio.org>`_ is the brains behind any of this.  It is a C (I
think) library that does all of the mathy stuff with the audio samples. It has
Python wrappers thankfully that made this possible. I barely understand any of
the terminology, and the documentation is really just looking at the
Python code examples, but it pretty much did everything I wanted it
to do. Installation was a bit of trial, and I cannot seem to get it
to build for Python 3.5 for anything. I'm also concerned about a
possibly memory leak in the phase vocoder, but there's a very good
chance it's my lack of knowledge that is causing it.

mido
====
The `mido <https://mido.readthedocs.org/en/latest/>`_ package is a great
example of a well-documented and simple-to-use library for dealing with MIDI
messages. I'd love it if this fumbling efforts of this project made it over
into this universe to grow up and be loved.