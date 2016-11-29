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

"""Class containing the Macro class."""

from textwrap import dedent

from scripting.key import key_name

class Macro:

    """A macro object.

    In a MUD client terminology, a macro is a link between a shortcut
    key and an action that is sent to the MUD.  For example, the F1
    shortcut could send 'north' to the MUD.

    """

    def __init__(self, key, modifiers, action, sharp=None):
        self.key = key
        self.modifiers = modifiers
        self.action = dedent(action.strip("\n"))
        self.sharp_engine = sharp

        # Set the trigger's level
        if sharp:
            self.level = sharp.engine.level
        else:
            self.level = None

    def __repr__(self):
        return "<Macro {}: {} (level={})>".format(self.shortcut,
                self.action, self.level.name)

    @property
    def shortcut(self):
        """Return the key name."""
        return key_name(self.key, self.modifiers)

    @property
    def sharp_script(self):
        """Return the SharpScript code to create this macro."""
        return self.sharp_engine.format((("#macro", self.shortcut,
                self.action), ))

    @property
    def copied(self):
        """Return another object of the Macro class with identical info."""
        copy = Macro(self.key, self.modifiers, self.action,
                self.sharp_engine)
        copy.level = self.level
        return copy

    def execute(self, engine, client):
        """Execute the macro."""
        self.sharp_engine.execute(self.action, variables=True)
