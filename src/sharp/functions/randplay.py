# Copyright (c) 2016, LE GOFF Vincent
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

"""Module containing the RandPlay function class."""

import os
from random import choice

import wx
from ytranslate import t

from log import logger
from sharp import Function

class RandPlay(Function):

    """Function SharpScript 'randplay'.

    This function plays a random sound from a list.

    """

    description = "Play a sound from a list at random"

    def run(self, filenames):
        """Play the audio file."""
        log = logger("sharp")
        if not filenames:
            return

        filenames = filenames.split(";")
        filename = choice(filenames)
        if self.engine.sounds:
            log.debug("#randplay {}".format(repr(filename)))
        else:
            log.debug("#randplay-silent {}".format(repr(filename)))
            return

        filename = self.find_abs_filename(filename)
        if os.path.exists(filename):
            log.debug("#randplay playing {}".format(repr(filename)))
        else:
            log.warning("#randplay cannot find the file at {}".format(
                    repr(filename)))

        sound = mixer.Sound(filename)
        sound.play()

    def find_abs_filename(self, filename):
        """Return the absolute path of the file.

        The initial file name can be absolute, or relative to the
        world's location.

        """
        if os.path.isabs(filename):
            pass
        elif os.path.normpath(filename).split(os.path.sep)[0] == "worlds":
            filename = os.path.abspath(filename)
        else:
            path = os.path.join(self.world.path, filename)
            filename = os.path.abspath(path)

        return filename

    def find_rel_filename(self, filename):
        """Return the filename relative to the world's location."""
        location = os.path.abspath(self.world.path)
        return os.path.relpath(filename, location)
