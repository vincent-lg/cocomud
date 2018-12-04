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
from twisted.internet import ssl, reactor

from client import CocoFactory
from config import Settings
from log import logger, begin
from sharp.engine import SharpScript
from world import World, MergingMethod

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

    def __init__(self, config_dir="."):
        self.logger = logger("")
        begin()
        self.config_dir = config_dir
        if config_dir != ".":
            self.logger.info(f"Using an alternative config directory: {config_dir}")

        self.settings = Settings(self, config_dir)
        self.sounds = True
        self.worlds = {}
        self.default_world = None
        self.level = Level.engine
        self.logger.info("CocoMUD engine started")

    def load(self):
        """Load the configuration."""
        self.logger.info("Loading the user's configuration...")
        self.settings.load()
        self.TTS_on = self.settings["options.TTS.on"]
        self.TTS_outside = self.settings["options.TTS.outside"]

        # For each world, set the game engine
        for world in self.worlds.values():
            world.engine = self

    def open(self, host, port, world, panel=None):
        """Connect to the specified host and port.

        This method creates and returns a 'Factory' class initialized
        with the specified information.  It also tries to connect a
        client to this factory.

        """
        self.logger.info("Creating a client for {host}:{port}".format(
                host=host, port=port))

        self.prepare_world(world)
        factory = CocoFactory(world, panel)

        if world.protocol.lower() == "ssl":
            reactor.connectSSL(host, port, factory,
                    ssl.ClientContextFactory())
        else:
            reactor.connectTCP(host, port, factory)

        return factory

    def open_help(self, name):
        """Open the selected help file in HTML format.

        This method open the browser with the appropriate file.
        The file is the one in the user's language, unless it cannot
        be found.

        """
        lang = self.settings.get_language()
        filename = name + ".html"
        path = os.path.join(self.config_dir, "doc", lang, filename)
        if os.path.exists(path):
            self.logger.debug("Open the help file for {} (lang={})".format(
                    name, lang))
            os.startfile(path)
            return

        # Try English
        path = os.path.join(self.config_dir, "doc", "en", filename)
        if os.path.exists(path):
            self.logger.debug("Open the help file for {} (lang=en)".format(
                    name))
            os.startfile(path)
            return

        # Neither worked
        self.logger.warning("The documentation for the {} help file " \
                "cannot be found, either using lang={} or lang=en".format(
                name, lang))

    def get_world(self, name):
        """Return the selected world either by its name or location."""
        name = name.lower()
        for world in self.worlds.values():
            if world.name.lower() == name:
                return world
            elif world.location == name:
                return world

        return None

    def create_world(self, name):
        """Create a world."""
        world = World(name.lower())
        world.engine = self
        return world

    def prepare_world(self, world, merge=None):
        """Prepare the world, creating appropriate values."""
        if not world.sharp_engine:
            sharp_engine = SharpScript(self, None, world)
            world.sharp_engine = sharp_engine

        if merge is not None:
            if merge == "ignore":
                world.merging = MergingMethod.ignore
            elif merge == "replace":
                world.merging = MergingMethod.replace
            else:
                raise ValueError("unkwno merging method: {}".format(
                        merge))

    def stop(self):
        """Stop the game engine and close the sessions."""
        reactor.stop()
