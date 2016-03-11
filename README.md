# soundtomidi
Python module that takes live sound, processes it, and generates 
semi-useful MIDI data from it.

Overview
========
This started with what seemed like a simple idea--use live audio to modify
the output of some LEDs. Which if you've been down this path, you come to
realize that the LED part (or DMX/ArtNet) is actually the easy part. It's
getting some form of useful information about the audio in the first place
that can be challenging.

I don't want to do this again, so after many different ways of trying this,
decided the most useful approach would be to create a single program to handle
all of the audio stuff and then turn that into some actionable MIDI output
data that I can play with. MIDI seemed like the best candidate for the job
since many light control programs, like DMXIS and QLC+, already have hooks for
listening to incoming MIDI data. It is rather inefficient when this program
is running on the same computer as the receiving software, but my idea is to
put this program on Raspberry PI or Beagle Bone and just let it live a very
stressed out life of doing nothing but listening to audio and putting out
MIDI messages. Which must be a depressing life for a circuit board.

As it stands now, from live audio you can get the following information from
the live sound:

+  The beat
+  The beats-per-minute (BPM)
+  The fundamental pitch
+  The root-mean-square (RMS)
+  The strength of various frequency bands (think graphic equalizer)

Is it accurate? Well, that depends. It took me a whole lot of tweaking to
figure out how much data each of the audio processors actually needs to get
the best results. So, the sounddevice deals with very short frames of data
and each audio processor accumulates some multiple of that, as well as a hop
size (that I only barely understand what it means). But, even through a mic,
the beat and BPM values look pretty solid. The fundamental pitch more or less
works too when I play a keyboard in the room next to the mic. There's a good
chance the RMS is being calculated wrong, so there's that. The frequency
bands seem to be about right when I play an increasing sine wave of all audio
frequencies from 20-20000 (search YouTube for "hearing test").

Is it efficient? No! Clearly all of the audio processors could share the
same set of incoming audio data without making copies of it. They started that
way, but it turns out that the best size of an audio frame for finding a beat
is much different than the best size for calculating frequency strengths for
the 31 octave bands. The code got so jumbled up that in the end I decided
to just let each of these audio processor workers have their own copy of the
audio data to do the nefarious things they want to do with it.

In the end, it is accurate enough information for my purposes, which is just
to make some lights react to live audio sounds. And if your purpose is
something along those lines and reading about what to do with the imaginary
number part of a FFT transformation is making you wish you stayed awake
in calculus class, this may be useful to you too.

