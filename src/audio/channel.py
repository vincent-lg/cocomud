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

"""Module containing the `Channel` class.

A channel is a named slot playing one sound at a time, such as "music"
or "weather".  Playing a sound in a channel replaces the sound it was
playing, fading it out if the channel has a fade duration, unless it's
the same file.  Channels are used by scripts and plugins; the user
tunes categories instead.

"""

import os

class Channel:

    """A named slot playing one sound at a time.

    Channels are created by `AudioLib.channel`.  The channel's
    category is used for its sounds, unless `play` is given another one.

    """

    def __init__(self, library, name, category=None, fade=0):
        self.library = library
        self.name = name
        self.category = category
        self.fade = fade
        self.sound = None

    def __repr__(self):
        return f"<Channel {self.name!r}, filename={self.filename!r}>"

    @property
    def filename(self):
        """Return the file this channel plays, or None.

        A sound that has stopped, or is fading out, doesn't count.

        """
        sound = self.sound
        if sound is None or sound.stopped or sound.fading_out:
            return None

        return sound.filename

    @property
    def volume(self):
        """Return the volume of the current sound, or None."""
        return self.sound.volume if self.sound else None

    @volume.setter
    def volume(self, volume):
        """Change the volume of the current sound."""
        if self.sound:
            self.sound.volume = volume

    @property
    def pan(self):
        """Return the pan of the current sound, or None."""
        return self.sound.pan if self.sound else None

    @pan.setter
    def pan(self, pan):
        """Change the pan of the current sound."""
        if self.sound:
            self.sound.pan = pan

    def play(self, filename, volume=100, pan=0, loop=False, delay=0,
            fade_in=0, fade=None, restart=False, category=None):
        """
        Play a file in this channel, replacing the current sound.

        If the channel already plays this file, nothing happens and
        the current sound is returned, unless `restart` is set.

        Args:
            filename (str): the path of the audio file.
            volume (int, optional): the sound's volume (0 to 100).
            pan (int, optional): the pan (-100 to 100).
            loop (bool, optional): should the sound loop?
            delay (float, optional): seconds to wait before playing.
            fade_in (float, optional): seconds to fade the new sound in.
            fade (float, optional): seconds to fade the old sound out,
                    the channel's `fade` by default.
            restart (bool, optional): play even if it's the same file.
            category (str or Category, optional): the channel's
                    category by default.

        Returns:
            sound (Sound): the sound playing in this channel.

        """
        current = self.filename
        if not restart and current and same_file(current, filename):
            return self.sound

        self.stop(fade)
        if category is None:
            category = self.category

        self.sound = self.library.play(filename, category=category,
                volume=volume, pan=pan, loop=loop, delay=delay,
                fade_in=fade_in)
        return self.sound

    def stop(self, fade=None):
        """
        Stop the current sound.

        Args:
            fade (float, optional): seconds to fade out before stopping,
                    the channel's `fade` by default.

        """
        sound, self.sound = self.sound, None
        if sound is None:
            return

        fade = self.fade if fade is None else fade
        if fade > 0:
            sound.fade_out(fade)
        else:
            sound.stop()

    def pause(self):
        """Pause the current sound."""
        return self.sound.pause() if self.sound else False

    def resume(self):
        """Unpause the current sound."""
        return self.sound.resume() if self.sound else False


def same_file(first, second):
    """Return whether two paths lead to the same file."""
    def normalize(path):
        return os.path.normcase(os.path.abspath(path))

    return normalize(first) == normalize(second)
