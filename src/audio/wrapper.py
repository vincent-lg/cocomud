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

"""Module containing the Python wrapper around the BASS library.

This module contains the `AudioLib` class.  It is not likely you will need to
import this module and manually create an instance of `AudioLib`, although
you can.  It's more likely you will import a single, preset instance of
`AudioLib`:

    from audio import audiolib

    # Use the AudioLib's methods on the `audiolib` object

"""

from audio import pybass
from audio.category import Category
from audio.channel import Channel
from audio.sound import Sound, call_from_thread, call_later

class AudioLib:

    """
    The wrapper for communication with the BASS library to play sounds.

    Attributes:
        categories: a dictionary of name: Category.
        channels: a dictionary of name: Channel.
        volume: the master volume (0 to 100).

    Methods on this object:
        play: play an audio file, creating a Sound object.
        stop: stop all audio files, or the ones of a category.
        category: get or create a category.
        channel: get or create a channel.

    """

    def __init__(self):
        self.has_init = False
        self.categories = {}
        self.channels = {}
        self.call_later = call_later
        self.call_from_thread = call_from_thread
        self._volume = 100
        self._sounds = set()

    def _init(self):
        """If not initialized, init the library."""
        if not self.has_init:
            self.has_init = pybass.BASS_Init(-1, 44100, 0, 0, 0)
            pybass.BASS_PluginLoad(b'bass_aac.dll', 0)
            pybass.BASS_PluginLoad(b'bass_ac3.dll', 0)
            pybass.BASS_PluginLoad(b'bass_aix.dll', 0)
            pybass.BASS_PluginLoad(b'bass_ape.dll', 0)
            pybass.BASS_PluginLoad(b'bass_mpc.dll', 0)
            pybass.BASS_PluginLoad(b'bass_ofr.dll', 0)
            pybass.BASS_PluginLoad(b'bass_spx.dll', 0)
            pybass.BASS_PluginLoad(b'bass_tta.dll', 0)
            pybass.BASS_PluginLoad(b'basscd.dll', 0)

            # Set channels to unicode mode (I don't know if it's necessary)
            pybass.BASS_CHANNELINFO._fields_.remove(('filename', pybass.ctypes.c_char_p))
            pybass.BASS_CHANNELINFO._fields_.append(('filename', pybass.ctypes.c_wchar_p))

    @property
    def volume(self):
        """Return the master volume (0 to 100)."""
        return self._volume

    @volume.setter
    def volume(self, volume):
        """Change the master volume, even for playing sounds."""
        self._volume = volume
        for sound in self.sounds:
            sound.update_gain()

    @property
    def sounds(self):
        """Return the sounds that haven't stopped yet."""
        self._sounds = {sound for sound in self._sounds if not sound.stopped}
        return list(self._sounds)

    def register(self, sound):
        """Keep track of a sound that starts, until it stops."""
        self._sounds.add(sound)

    def category(self, name, volume=None, label=None):
        """
        Return a category, creating it if needed.

        Args:
            name (str): the category name, like "combat".
            volume (int, optional): if set, change the category volume.
            label (str, optional): if set, change the name shown to users.

        Returns:
            category (Category): the category with this name.

        """
        category = self.categories.get(name)
        if category is None:
            category = Category(self, name)
            self.categories[name] = category

        if volume is not None:
            category.volume = volume
        if label is not None:
            category.label = label

        return category

    def channel(self, name, category=None, fade=None):
        """
        Return a channel, creating it if needed.

        Args:
            name (str): the channel name, like "music".
            category (str or Category, optional): if set, change the
                    category used for the channel's sounds.
            fade (float, optional): if set, change the fade-out duration
                    used when a sound replaces another.

        Returns:
            channel (Channel): the channel with this name.

        """
        channel = self.channels.get(name)
        if channel is None:
            channel = Channel(self, name)
            self.channels[name] = channel

        if category is not None:
            channel.category = category
        if fade is not None:
            channel.fade = fade

        return channel

    def play(self, path, category=None, volume=100, pan=0, loop=False,
            delay=0, fade_in=0):
        """
        Load an audio file, play it and return a Sound object.

        Args:
            path (str): the path leading to the audio file.
            category (str or Category, optional): the sound category,
                    created if needed.
            volume (int, optional): the sound's volume (0 to 100).
            pan (int, optional): the pan (-100 to 100).
            loop (bool, optional): should the sound loop?
            delay (float, optional): seconds to wait before playing.
            fade_in (float, optional): seconds to fade in from silence.

        Returns:
            sound (Sound): the Sound object.  If the file couldn't be
            played, the sound is stopped and its `error` attribute
            describes the problem.

        """
        self._init()
        if isinstance(category, str):
            category = self.category(category)

        sound = Sound(path, library=self, category=category, volume=volume,
                pan=pan, loop=loop)
        sound.play(delay=delay, fade_in=fade_in)
        return sound

    def stop(self, category=None, fade=0):
        """
        Stop all sounds, or the sounds of a category.

        Args:
            category (str or Category, optional): the category to stop.
            fade (float, optional): seconds to fade out before stopping.

        """
        if isinstance(category, str):
            category = self.categories.get(category)
            if category is None:
                return

        for sound in self.sounds:
            if category is None or sound.category is category:
                if fade > 0:
                    sound.fade_out(fade)
                else:
                    sound.stop()
