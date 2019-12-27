# Copyright (c) 2016-2020, LE GOFF Vincent
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

"""

from enum import Enum

from audio import pybass

class Sound:

    """A sound class, to define the sounds objects."""

    def __init__(self, filename):
        self.filename = filename
        self.bass_handle = None

    def __repr__(self):
        return f"<Sound filename={self.filename!r}, status={self.status}>"

    @property
    def status(self):
        """Return the current status."""
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

    def play(self):
        """
        Start playing or unpause this sound.

        Returns:
            playing (bool): whether this sound now is playing.

        """
        if self.stopped:
            filename = self.filename
            try:
                filename = filename.encode("utf-8")
            except UnicodeError:
                return False

            # Get a handle on the file
            self.bass_handle = pybass.BASS_StreamCreateFile(False, filename, 0, 0, 0)
        elif not self.paused:
            return False

        # Start playing the sound
        pybass.BASS_ChannelPlay(self.bass_handle, False)
        return self.playing

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

    def stop(self):
        """
        Stop the playing audio file.

        Returns:
            stopped (bool): has this sound stopped?

        """
        if not self.playing:
            return False

        pybass.BASS_ChannelStop(self.bass_handle)
        return self.stopped


class PlayingStatus(Enum):

    """Enumeration to describe individual file playing status."""

    UNKNOWN = "unknown status"
    STOPPED = "stopped"
    PLAYING = "currently playing"
    STALLED = "stalled"
    PAUSED = "paused"


STATUSES = {
        pybass.BASS_ACTIVE_STOPPED: PlayingStatus.STOPPED,
        pybass.BASS_ACTIVE_PLAYING: PlayingStatus.PLAYING,
        pybass.BASS_ACTIVE_STALLED: PlayingStatus.STALLED,
        pybass.BASS_ACTIVE_PAUSED: PlayingStatus.PAUSED,
}
