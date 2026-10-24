# Copyright (c) 2016-2026, LE GOFF Vincent
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.

# * Neither the name of ytranslate nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Module containing the `Sound` class.

A `Sound` object represents an audio file, whether currently playing or not.
Methods on that file allow to interact with audio.

Volumes go from 0 to 100, pans from -100 (left) to 100 (right), and
durations are in seconds.  The volume heard is the master volume x
the category's volume x the sound's own volume.  The sound's own
volume is set on `BASS_ATTRIB_VOL`, which fades slide.  The master and
category volumes are set on `BASS_ATTRIB_VOLDSP`, so that changing them
doesn't interrupt a fade.

"""

from enum import Enum

from audio import pybass

def call_later(delay, function, *args):
    """Call a function in `delay` seconds, using the Twisted reactor.

    The reactor is imported here, not at the top of the module, so
    that importing the audio package doesn't install the default
    reactor before CocoMUD installs `wxreactor`.

    """
    from twisted.internet import reactor
    return reactor.callLater(delay, function, *args)

def call_from_thread(function, *args):
    """Call a function in the main thread, from another thread."""
    from twisted.internet import reactor
    reactor.callFromThread(function, *args)


class Sound:

    """A sound class, to define the sounds objects.

    Most of the time, sounds are created and played by
    `AudioLib.play`.  The volume, pan and loop of a sound can be
    changed while it plays.

    """

    def __init__(self, filename, library=None, category=None, volume=100,
            pan=0, loop=False):
        self.filename = filename
        self.library = library
        self.category = category
        self.bass_handle = None
        self.error = None
        self._volume = volume
        self._pan = pan
        self._loop = loop
        self._on_end = None
        self._sync = None
        self._pending = None
        self._fade_call = None

    def __repr__(self):
        return f"<Sound filename={self.filename!r}, status={self.status}>"

    @property
    def status(self):
        """Return the current status."""
        if self._pending:
            return PlayingStatus.PENDING

        if self.bass_handle:
            status = pybass.BASS_ChannelIsActive(self.bass_handle)
        else:
            status = 0

        return STATUSES.get(status, PlayingStatus.UNKNOWN)

    @property
    def stopped(self):
        return self.status == PlayingStatus.STOPPED

    @property
    def playing(self):
        return self.status == PlayingStatus.PLAYING

    @property
    def stalled(self):
        return self.status == PlayingStatus.STALLED

    @property
    def paused(self):
        return self.status == PlayingStatus.PAUSED

    @property
    def pending(self):
        """Is this sound waiting for its delay before playing?"""
        return self.status == PlayingStatus.PENDING

    @property
    def fading_out(self):
        """Is this sound fading out before it stops?"""
        return self._fade_call is not None

    @property
    def volume(self):
        """Return the sound's own volume (0 to 100)."""
        return self._volume

    @volume.setter
    def volume(self, volume):
        """Change the volume, interrupting any fade."""
        self._cancel_fade_out()
        self._volume = volume
        self._set_attribute(pybass.BASS_ATTRIB_VOL, volume / 100)

    @property
    def pan(self):
        """Return the pan (-100 for left, 100 for right)."""
        return self._pan

    @pan.setter
    def pan(self, pan):
        """Change the pan, interrupting any pan fade."""
        self._pan = pan
        self._set_attribute(pybass.BASS_ATTRIB_PAN, pan / 100)

    @property
    def loop(self):
        """Return whether the sound loops."""
        return self._loop

    @loop.setter
    def loop(self, loop):
        """Make the sound loop or not, even while it plays."""
        self._loop = loop
        if self.bass_handle:
            flags = pybass.BASS_SAMPLE_LOOP if loop else 0
            pybass.BASS_ChannelFlags(self.bass_handle, flags,
                    pybass.BASS_SAMPLE_LOOP)

    @property
    def gain(self):
        """Return the factor of the master and category volumes (0 to 1)."""
        gain = 1
        if self.library:
            gain = self.library.volume / 100

        if self.category:
            gain *= self.category.gain

        return gain

    @property
    def on_end(self):
        """Return the callback called when the sound reaches its end."""
        return self._on_end

    @on_end.setter
    def on_end(self, callback):
        """Set a callback, called with the sound when it reaches its end.

        The callback is called in the main thread.  It isn't called
        when the sound is stopped.  For a looping sound, it is called
        at the end of each pass.

        """
        self._on_end = callback
        if callback and self.bass_handle and not self._sync:
            self._set_sync()

    def play(self, delay=0, fade_in=0):
        """
        Start playing or unpause this sound.

        Args:
            delay (float, optional): seconds to wait before playing.
            fade_in (float, optional): seconds to fade in from silence.

        Returns:
            playing (bool): whether this sound now is playing (or will
            play after the delay).

        """
        if self.paused:
            pybass.BASS_ChannelPlay(self.bass_handle, False)
            return self.playing
        elif not self.stopped:
            return False

        if self.library:
            self.library.register(self)

        if delay > 0:
            scheduler = self.library.call_later if self.library else call_later
            self._pending = scheduler(delay, self._start, fade_in)
            return True

        return self._start(fade_in)

    def pause(self):
        """
        Pause the sound, if it's currently playing.

        Returns:
            paused (bool): whether this sound has been paused or not.

        """
        if not self.playing:
            return False

        pybass.BASS_ChannelPause(self.bass_handle)
        return self.paused

    def resume(self):
        """
        Unpause the sound.

        Returns:
            resumed (bool): whether this sound is playing again.

        """
        if not self.paused:
            return False

        return self.play()

    def stop(self):
        """
        Stop the audio file, whether playing, paused or delayed.

        Returns:
            stopped (bool): has this sound stopped?

        """
        self._cancel_fade_out()
        if self._pending:
            self._pending.cancel()
            self._pending = None
            return True

        if self.stopped:
            return False

        pybass.BASS_ChannelStop(self.bass_handle)
        return self.stopped

    def fade(self, volume=None, pan=None, duration=1):
        """
        Slide the volume, the pan or both over some time.

        Args:
            volume (int, optional): the volume to reach (0 to 100).
            pan (int, optional): the pan to reach (-100 to 100).
            duration (float, optional): the fade duration in seconds.

        """
        milliseconds = int(duration * 1000)
        if volume is not None:
            self._cancel_fade_out()
            self._volume = volume
            self._slide(pybass.BASS_ATTRIB_VOL, volume / 100, milliseconds)

        if pan is not None:
            self._pan = pan
            self._slide(pybass.BASS_ATTRIB_PAN, pan / 100, milliseconds)

    def fade_out(self, duration=1):
        """
        Fade the sound out, then stop it.

        A paused or delayed sound is stopped right away.  The sound
        keeps its volume: if played again, it's heard at its volume.

        Args:
            duration (float, optional): the fade duration in seconds.

        Returns:
            stopping (bool): whether the sound is stopping.

        """
        if self.pending or self.paused or duration <= 0:
            return self.stop()
        elif self.stopped:
            return False

        self._cancel_fade_out()
        self._slide(pybass.BASS_ATTRIB_VOL, 0, int(duration * 1000))
        scheduler = self.library.call_later if self.library else call_later
        self._fade_call = scheduler(duration, self._end_fade_out)
        return True

    def update_gain(self):
        """Apply the master and category volumes again."""
        self._set_attribute(pybass.BASS_ATTRIB_VOLDSP, self.gain)

    def _start(self, fade_in=0):
        """Create the stream and play it."""
        self._pending = None
        try:
            filename = self.filename.encode("utf-8")
        except UnicodeError:
            self.error = "the file name can't be encoded"
            return False

        flags = pybass.BASS_STREAM_AUTOFREE
        if self._loop:
            flags |= pybass.BASS_SAMPLE_LOOP

        handle = pybass.BASS_StreamCreateFile(False, filename, 0, 0, flags)
        if not handle:
            self.error = pybass.get_error_description(
                    pybass.BASS_ErrorGetCode())
            return False

        self.bass_handle = handle
        self.error = None
        self._sync = None
        volume = 0 if fade_in > 0 else self._volume / 100
        self._set_attribute(pybass.BASS_ATTRIB_VOL, volume)
        self._set_attribute(pybass.BASS_ATTRIB_PAN, self._pan / 100)
        self.update_gain()
        if self._on_end:
            self._set_sync()

        pybass.BASS_ChannelPlay(handle, False)
        if fade_in > 0:
            self._slide(pybass.BASS_ATTRIB_VOL, self._volume / 100,
                    int(fade_in * 1000))

        return self.playing

    def _set_attribute(self, attribute, value):
        """Set an attribute, if the stream exists."""
        if self.bass_handle:
            pybass.BASS_ChannelSetAttribute(self.bass_handle, attribute,
                    value)

    def _slide(self, attribute, value, milliseconds):
        """Slide an attribute, if the stream exists."""
        if self.bass_handle:
            pybass.BASS_ChannelSlideAttribute(self.bass_handle, attribute,
                    value, milliseconds)

    def _set_sync(self):
        """Ask BASS to call `on_end` when the stream ends.

        BASS calls the sync procedure in one of its threads, so the
        callback is forwarded to the main thread.  The `SYNCPROC` is
        kept on the sound: ctypes would free it otherwise, and BASS
        would call freed memory.

        """
        forward = self.library.call_from_thread if self.library else \
                call_from_thread

        def ended(sync, channel, data, user):
            forward(self._ended)

        self._sync = pybass.SYNCPROC(ended)
        pybass.BASS_ChannelSetSync(self.bass_handle, pybass.BASS_SYNC_END,
                0, self._sync, None)

    def _ended(self):
        """The stream has reached its end."""
        if self._on_end:
            self._on_end(self)

    def _cancel_fade_out(self):
        """Cancel the stop planned at the end of a fade-out."""
        if self._fade_call:
            self._fade_call.cancel()
            self._fade_call = None

    def _end_fade_out(self):
        """The fade-out is over, stop the sound."""
        self._fade_call = None
        self.stop()


class PlayingStatus(Enum):

    """Enumeration to describe individual file playing status."""

    UNKNOWN = "unknown status"
    STOPPED = "stopped"
    PLAYING = "currently playing"
    STALLED = "stalled"
    PAUSED = "paused"
    PENDING = "waiting to play"


STATUSES = {
        pybass.BASS_ACTIVE_STOPPED: PlayingStatus.STOPPED,
        pybass.BASS_ACTIVE_PLAYING: PlayingStatus.PLAYING,
        pybass.BASS_ACTIVE_STALLED: PlayingStatus.STALLED,
        pybass.BASS_ACTIVE_PAUSED: PlayingStatus.PAUSED,
}
