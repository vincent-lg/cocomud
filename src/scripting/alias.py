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

"""Class containing the Alias class."""

import re

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
        self.action = action

        # Set the alias's level
        self.level = sharp.engine.level

    def __repr__(self):
        return "<Alias for {} (level={})>".format(
                repr(self.alias), self.level.name)

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

    def test(self, command):
        """Should the alias be triggered by the text?"""
        if self.re_alias.search(command):
            self.execute()
            return True

        return False

    def execute(self):
        """Execute the alias."""
        self.sharp_engine.execute(self.action)
