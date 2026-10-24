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

"""Module containing the `Category` class.

A category is a named group of sounds sharing a volume, such as
"combat" or "music".  Any number of sounds of the same category can
play at the same time.  Categories are what the user tunes: changing
the volume of a category, or muting it, applies to all its sounds,
including the ones already playing.

"""

class Category:

    """A named group of sounds sharing a volume.

    Categories are created by `AudioLib.category`.

    """

    def __init__(self, library, name, volume=100, label=None):
        self.library = library
        self.name = name
        self.label = label or name
        self._volume = volume
        self._muted = False

    def __repr__(self):
        muted = ", muted" if self._muted else ""
        return f"<Category {self.name!r}, volume={self._volume}{muted}>"

    @property
    def volume(self):
        """Return the category volume (0 to 100)."""
        return self._volume

    @volume.setter
    def volume(self, volume):
        """Change the volume of all the sounds in this category."""
        self._volume = volume
        self.update()

    @property
    def muted(self):
        """Return whether the category is muted."""
        return self._muted

    @muted.setter
    def muted(self, muted):
        """Mute or unmute the category, sounds keep on playing."""
        self._muted = muted
        self.update()

    @property
    def gain(self):
        """Return the volume factor of this category (0 to 1)."""
        return 0 if self._muted else self._volume / 100

    @property
    def sounds(self):
        """Return the sounds of this category that haven't stopped."""
        return [sound for sound in self.library.sounds
                if sound.category is self]

    def update(self):
        """Apply the category volume to its sounds."""
        for sound in self.sounds:
            sound.update_gain()

    def stop(self, fade=0):
        """Stop all the sounds of this category.

        Args:
            fade (float, optional): seconds to fade out before stopping.

        """
        self.library.stop(category=self, fade=fade)
