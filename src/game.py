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

"""This file contains the GameEngine class."""

import os

from enum import Enum

from client import GUIClient
from config import Settings
from sharp.engine import SharpScript

class Level(Enum):

    """Enumeration for a feature level.

    Features at the top level have the value "engine". They will be
    common across all worlds and characters. Features are often defined
    at the world level (common across characters) or at the character
    level (specific to this character).

    For instance, look at the macros, triggers and aliases.

    """

    engine = 1
    world = 2
    character = 3
    category = 4


class GameEngine:

    """A class representing the game engine.

    An instance of this class is to be created each time the program
    runs.  It doesn't handle thegraphical user interface, but centralizes
    about anything else:  the main configuration, world configuration
    of different games, aliases, macros, triggers and so on.  The
    GUI has a direct access to the engine and can therefore access it.

    """

    def __init__(self):
        self.settings = Settings(self)
        self.worlds = {}
        self.default_world = None
        self.level = Level.engine

    def load(self):
        """Load the configuration."""
        self.settings.load()
        self.TTS_on = self.settings["options.TTS.on"]
        self.TTS_outside = self.settings["options.TTS.outside"]

        # For each world, set the game engine
        for world in self.worlds.values():
            world.engine = self

    def open(self, host, port, world):
        """Connect to the specified host and port.

        This method creates and returns a 'GUIClient' class initialized
        with the specified information.

        """
        client = GUIClient(host, port, engine=self, world=world)
        sharp_engine = SharpScript(self, client, world)
        world.client = client
        client.sharp_engine = sharp_engine
        world.sharp_engine = sharp_engine
        return client

    def open_help(self, name):
        """Open the selected help file in HTML format.

        This method open the browser with the appropriate file.
        The file is the one in the user's language, unless it cannot
        be found.

        """
        lang = self.settings.get_language()
        filename = name + ".html"
        path = os.path.join("doc", lang, filename)
        if os.path.exists(path):
            os.startfile(path)
            return

        # Try English
        path = os.path.join("doc", "en", filename)
        if os.path.exists(path):
            os.startfile(path)
            return

        # Neither worked
        raise ValueError("the doc {} cannot be found, either in the " \
                "user's language or English".format(repr(name)))
