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

"""Audio library, to play sounds in various formats.

This package includes:
-  The `pybass` library, to play sounds using `BASS`, a thitd-party library
   with its own license.
-  A wrapper around the `pybass` library to make it easy to use `BASS` from
   CocoMUD.

Notice that, even though this package could be useful in other projects,
it is not released as a separate library and doesn't attempt to be used
outside of CocoMUD.  Hence, for instance, the wrapper is built with
Python 3.6 in mind and doesn't have any particular checks to be
compatible with other Python versions.

Wrapper usage:
1. From within CocoMUD, just import the wrapper:
       from audio import audiolib
2. `audiolib` is an instance of `AudioLib`, the wrapper used to
   communicate with `pybass`.  Therefore, `audiolib` could be considered
   as a standalone, although you could in theory create other objects
   of this class.
3. You can then use the methods of the `audiolib` instance to play sounds
   (see below).

Example:
    from audio import audiolib

    audiolib.play("path/of/my/file.ogg")
    # Or alternatively, to keep a handle on the played sound
    import time
    sound = audiolib.play("path/of/my/file.ogg")
    time.sleep(2) # notice that the sound will keep on playing while Python pauses
    sound.pause()
    sound.stop()
    sound.volume = 80 # 80% of volume
    sound.play() # unpause the sound

Frequently used methods:

- `AudioLib.play(str)`: play a sound, given the file path to access it.  `BASS` supports WAV, MP3, OGG and other formats (see the full documentation).
- `AudioLib.stop()`: stop all sounds that are currently playing.
- `Sound.play()`: start playing or unpause a sound.
- `Sound.pause()`: pause a sound.
- `Sound.stop()`: stop a sound.

"""

from audio.wrapper import AudioLib

audiolib = AudioLib()
