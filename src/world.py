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

"""This file contains the World class."""

from codecs import open
import os
from textwrap import dedent

from configobj import ConfigObj

class World:

    """A class representing a World object.

    A world is a game (a server).  It conatins a hostname and a port
    and optionally characters.

    """

    def __init__(self, location):
        self.location = location
        self.name = ""
        self.hostname = ""
        self.port = 4000
        self.characters = {}
        self.settings = None

        # World's access to general data
        self.client = None
        self.engine = None
        self.sharp_engine = None

        # World's configuration
        self.aliases = []
        self.macros = []
        self.triggers = []

    def __repr__(self):
        return "<World {} (hostname={}, port={})>".format(
                self.name, self.hostname, self.port)

    @property
    def path(self):
        return "worlds/" + self.location

    def load(self):
        """Load the config.set script."""
        from game import Level
        level = self.engine.level
        self.engine.level = Level.world
        path = self.path
        path = os.path.join(path, "config.set")
        if os.path.exists(path):
            file = open(path, "r", encoding="latin-1", errors="replace")
            content = file.read().replace("\r", "")
            file.close()

            # Execute the script
            self.sharp_engine.execute(content)

        # Put the engine level back
        self.engine.level = level

    def save(self):
        """Save the world in its configuration file."""
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        spec = dedent("""
            [connection]
                name = "unknown"
                hostname = "unknown.ext"
                port = 0
        """).strip("\n")

        if self.settings is None:
            self.settings = ConfigObj(spec.split("\n"))

        connection = self.settings["connection"]
        connection["name"] = self.name
        connection["hostname"] = self.hostname
        connection["port"] = self.port
        self.settings.filename = os.path.join(self.path, "options.conf")
        self.settings.write()
        self.save_config()

    def save_config(self):
        """Save the 'config.set' script file."""
        lines = []

        # Aliases
        for alias in self.aliases:
            lines.append(alias.sharp_script)

        # Macros
        for macro in self.macros:
            lines.append(macro.sharp_script)

        # Triggers
        for trigger in self.triggers:
            lines.append(trigger.sharp_script)

        content = "\n".join(lines) + "\n"
        content = content.replace("\n", "\r\n")
        path = self.path
        path = os.path.join(path, "config.set")
        file = open(path, "w", encoding="latin-1", errors="replace")
        file.write(content)
        file.close()
