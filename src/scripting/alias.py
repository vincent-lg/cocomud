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

"""Class containing the Alias class."""

import re
from textwrap import dedent

from log import logger

class Alias:

    """An alias object.

    In a MUD client terminology, an alias is here to speed up command
    inputs by associating a certain (short) command with a desired
    input.  For instance, "co" could be associated with "crew order".

    """

    def __init__(self, sharp, alias, action):
        self.sharp_engine = sharp
        self.alias = alias
        self.re_alias = self.find_regex(alias)
        self.action = dedent(action.strip("\n"))

        # Set the alias's level
        self.level = sharp.engine.level

    def __repr__(self):
        return "<Alias for {} (level={})>".format(
                repr(self.alias), self.level.name)

    @property
    def sharp_script(self):
        """Return the SharpScript code to create this alias."""
        return self.sharp_engine.format((("#alias", self.alias,
                self.action), ))

    def find_regex(self, alias):
        """Find and compile the alias given as argument.

        If the alias begins with '^', the alias is already a
        regular expression that just needs to be compiled.  Otherwise,
        some automatic actions will be performed on it.

        """
        if alias.startswith("^"):
            return re.compile(alias)

        alias = re.escape(alias)

        # The '*' sign will be replaced by a group
        alias = alias.replace("\\*", "(.*?)")
        alias = "^" + alias + "$"

        return re.compile(alias, re.IGNORECASE)

    @property
    def copied(self):
        """Return a copied version of the alias."""
        copy = Alias(self.sharp_engine, self.alias, self.action)
        copy.level = self.level
        return copy

    def test(self, command):
        """Should the alias be triggered by the text?"""
        match = self.re_alias.search(command)
        if match:
            log = logger("client")
            log.debug("Executing the alias {}".format(
                    repr(self.alias)))

            engine = self.sharp_engine
            if "args" not in engine.locals:
                engine.locals["args"] = {}

            args = engine.locals["args"]

            # Copy the groups of this match
            i = 0
            for group in match.groups():
                i += 1
                args[str(i)] = group

            # Copy the named groups
            for name, group in match.groupdict().items():
                engine.locals[name] = group

            # Execute the alias
            self.execute()
            return True

        return False

    def execute(self):
        """Execute the alias."""
        try:
            self.sharp_engine.execute(self.action, variables=True, debug=True)
        except Exception:
            log = logger("client")
            log.exception("An error occurred while executing the alias " \
                    "{}".format(repr(self.alias)))
