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

"""This file contains the Character class."""

import os

from log import character as logger
from safe import Safe

class Character:

    """An object to represent a character from a world.

    A world represents a game, with the information to reach the
    server.  A character, on the other hand, represents specific
    information to one player in this world.  Worlds may have no
    character (the default).  Characters can be set to keep login
    information safely, like the username and password and additional
    commands.

    Characters may have their specific configuration, like their
    specific set of aliases, macros or triggers.

    """

    def __init__(self, world, location):
        self.world = world
        self.location = location
        self.name = "unknown"
        self.username = ""
        self.password = ""
        self.other_commands = ""

        # Character's configuration
        self.aliases = []
        self.macros = []
        self.triggers = []

    def __repr__(self):
        return "<Character {} (world={}, location={})>".format(self.name,
                self.world and self.world.name or "unknown", self.location)

    def __str__(self):
        return self.name

    def create_safe(self):
        """Create a safe for this character."""
        location = os.path.join(self.world.path, self.location)
        if not os.path.exists(location):
            logger.info("Try to create the {} location for a character".format(
                    repr(location)))
            os.makedirs(location)

        # Create a safe for this character
        safe = Safe(file=os.path.join(location, ".passphrase"),
                secret=os.path.join(location, "login"))

        return safe

    def load(self):
        """Load the encrypted configuration.

        If present, it will be in {world}/{location}/{login}.
        The passphrase will be in {world}/{location}/.passphrase .

        """
        location = os.path.join(self.world.path, self.location)

        # Retrieve encrypted information
        safe = self.create_safe()
        self.name = safe.retrieve("name", "")
        self.username = safe.retrieve("username", "")
        self.password = safe.retrieve("password", "")
        self.other_commands = safe.retrieve("other_commands", "")

    def save(self):
        """Save the character."""
        safe = self.create_safe()
        safe.store("name", self.name)
        safe.store("username", self.username)
        safe.store("password", self.password)
        safe.store("other_commands", self.other_commands)
