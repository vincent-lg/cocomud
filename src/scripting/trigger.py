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

"""Class containing the Trigger class."""

import re

class Trigger:

    """A trigger object.

    In a MUD client terminology, a trigger can "watch" the information
    received by the client, and do something in return, like sending
    an information to the server, playing a sound, calling a script
    and so on.

    """

    def __init__(self, sharp, reaction, action):
        self.sharp_engine = sharp
        self.reaction = reaction
        self.re_reaction = self.find_regex(reaction)
        self.action = action
        if sharp and sharp.engine:
            self.logger = sharp.engine.loggers["cocomud.sharp"]
        else:
            self.logger = None

        # Set the trigger's level
        self.level = sharp.engine.level

    def __repr__(self):
        return "<Trigger for {} (level={})>".format(
                repr(self.reaction), self.level.name)

    @property
    def sharp_script(self):
        """Return the SharpScript code to create this trigger."""
        return self.sharp_engine.format((("#trigger", self.reaction,
                self.action), ))

    @property
    def copied(self):
        """Return a copied version of the trigger."""
        copy = Trigger(self.sharp_engine, self.reaction, self.action)
        copy.level = self.level
        return copy

    @property
    def world(self):
        """Return the world bound to the SharpEngine."""
        return self.sharp_engine and self.sharp_engine.world or None

    def find_regex(self, reaction):
        """Find and compile the reaction given as argument.

        If the reaction begins with '^', the reaction is already a
        regular expression that just needs to be compiled.  Otherwise,
        some automatic actions will be performed on it.

        """
        if reaction.startswith("^"):
            return re.compile(reaction)

        reaction = re.escape(reaction)

        # The '*' sign will be replaced by a group
        reaction = reaction.replace("\\*", "(.*?)")
        reaction = "^" + reaction + "$"

        return re.compile(reaction, re.IGNORECASE)

    def feed(self, line):
        """Should the trigger be triggered by the text?"""
        if self.re_reaction.search(line):
            if self.logger:
                world = self.world
                world = world and world.name or "unknown"
                self.logger.debug("Trigger {}.{} fired.".format(
                        world, self.reaction))

            self.execute()

    def execute(self):
        """Execute the trigger."""
        self.sharp_engine.execute(self.action)
