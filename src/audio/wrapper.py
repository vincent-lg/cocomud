# Copyright (c) 2018, LE GOFF Vincent
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
from audio.sound import Sound

class AudioLib:

    """
    The wrapper for communication with the BASS library to play sounds.

    Methods on this object:
        generate: generate a Sound object from this file, do not play it.
        play: play an audio file, creating a Sound object.
        stop: stops all audio files.

    """

    def __init__(self):
        self.has_init = False

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

    def play(self, path):
        """
        Load an audio file, play it and return a Sound object.

        Args:
            path (str): the path leading to the audio file.

        Returns:
            sound (Sound or None): the Sound object to the playing file, or
            `None` if an error occurred

        """
        self._init()
        sound = Sound(path)
        sound.play()
        return sound
