============
Installation
============

In theory, one should be able to install this with the usual::

    pip install soundtomidi

If you are able to do that, it's because a kind stranger on the internet has
decided to help me get through the packaging. I'm still struggling with the
differences between
`Markdown <https://daringfireball.net/projects/markdown/>`_ and
`Sphinx <http://www.sphinx-doc.org/en/stable/contents.html>`_ sphinx, and
I'm still not clear on the semantic differences between module/package/library.
(Python folks on StackOverflow are usually nicer than other languages, but
boy does this topic bring out some nasty folks.)

which python
============
This project relies heavily on the `aubio <http://aubio.org>`_ audio
processing library, which if desired, can create Python bindings. The way that
it creates these Python bindings seems to only work for a Python 2.x install.
Which is unfortunate. I've attempted to make the entire project easily portable
to a Python 3.x install, but for now, you'll need to stay in the 2.x world.

On OSX
======
This software was written on a Mac using a `brew'd <http://brew.sh>`_ version
of Python 2.7 and `virtualenv <https://pypi.python.org/pypi/virtualenv>`_.
Before installing the required Python packages, you'll may need to have some
things installed on your system.  The easiest way to do this is::

    brew install portaudio
    brew install rtmidi
    brew install --with-python aubio

Note this is done before activating a virtualenv environment. This puts the
aubio python packages into the /python/site-packages directory associated with
your brew Python install (/usr/local/Cellar likely).

If you setting up a virtualenv, do so now::

    mkvirtualenv project_name

Find the site-packages directory associated with this virtual environment and
copy the aubio directories from the brew install earlier into this directory.
Copy, don't move.  This is messy, but as mentioned earlier,
`aubio <http://aubio.org>`_ is a bit of an odd duck installation-wise.

Double check that you are able to import aubio into this virtual environment::

    python
    import aubio
    quit()

If you get no errors, you're nearly there. Sorry for the verbosity, but this
turned out to be one of the most challenging aspects of this project.

At this point, just::

    pip install -r requirements.txt

To install the rest.  Or if you want to do it yourself, you'll need:

* `numpy <http://www.numpy.org>`_
* `docopt <http://docopt.org>`_
* `python-sounddevice <http://python-sounddevice.readthedocs.org/en/0.3.1/>`_
* `mido <https://mido.readthedocs.org/en/latest/>`_

Note that
`python-sounddevice <http://python-sounddevice.readthedocs.org/en/0.3.1/>`_
relies on `port-audio <http://portaudio.com/docs/v19-doxydocs/index.html>`_,
and `mido <https://mido.readthedocs.org/en/latest/>`_ relies on
`rtmidi <http://www.music.mcgill.ca/~gary/rtmidi/>`_.
