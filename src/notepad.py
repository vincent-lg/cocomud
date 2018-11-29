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

"""Module containing the Notepad class."""

import os

from log import main as logger

class Notepad:

    """Object representing a world or character notepad.

    A notepad is just what it sounds like:  a text file that can be
    edited through the interface.  It is specific to a world or
    character.

    When a user opens the notepad, the content of the file is retrieved
    and a dialog box is open with this content.  When the user closes
    this notepad, it is saved.

    """

    def __init__(self, owner):
        self.owner = owner
        self.content = ""

    def __repr__(self):
        return "<Notepad owner by {}>".format(self.owner)

    @property
    def path(self):
        """Return the path leading to the notepad file."""
        return os.path.join(self.owner.path, "notepad.txt")

    def open(self, empty_string):
        """Open the notepad file, read it and close it.

        If the file doesn't exist, or if it is empty, the 'empty_string'
        is placed in it.

        """
        parentdir = self.owner.path
        location = self.path
        logger.info("Opening the notepad file at {}".format(location))

        # Try to pen the file
        if not os.path.exists(location):
            # Try to create it
            if not os.access(parentdir, os.W_OK):
                logger.warning("CocoMUD doesn't have the right to " \
                        "write in {}".format(parentdir))
            else:
                content = empty_string

                with open(location, "w", encoding="utf-8") as file:
                    file.write(content)

            self.content = empty_string
        else:
            if not os.access(location, os.R_OK):
                logger.warning("CocoMUD doesn't have the right to " \
                        "read {}".format(location))
            else:
                with open(location, "r", encoding="utf-8") as file:
                    content = file.read()

                self.content = content

    def save(self):
        """Save the notepad in its file."""
        parentdir = self.owner.path
        location = self.path
        logger.info("Saving the notepad file in {}".format(location))

        if not os.access(location, os.W_OK):
            logger.warning("CocoMUD doesn't have the right to write " \
                    "in {}".format(location))
        else:
            content = self.content
            with open(location, "w", encoding="utf-8") as file:
                file.write(content)
