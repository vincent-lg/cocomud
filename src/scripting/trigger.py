# Copyright (c) 2016-2020, LE GOFF Vincent
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

"""Class containing the Trigger class."""

import re
from textwrap import dedent

from log import sharp as logger
from scripting.pattern import pattern_to_regex

class Trigger:

    """A trigger object.

    In a MUD client terminology, a trigger can "watch" the information
    received by the client, and do something in return, like sending
    an information to the server, playing a sound, calling a script
    and so on.

    """

    def __init__(self, sharp, reaction, action, substitution=""):
        self.sharp_engine = sharp
        self.reaction = reaction
        self.re_reaction = self.find_regex(reaction)
        self.action = dedent(action.strip("\n"))
        self.substitution = substitution

        # Flags
        self.mute = False
        self.mark = False
        self.show_if = ""
        self.hide_if = ""
        self.logger = logger

        # Set the trigger's level
        self.level = sharp.engine.level

    def __repr__(self):
        return "<Trigger for {} (level={})>".format(
                repr(self.reaction), self.level.name)

    @property
    def sharp_script(self):
        """Return the SharpScript code to create this trigger."""
        arguments = [self.reaction, self.action]
        if self.substitution:
            arguments.append(self.substitution)

        flags = []
        if self.mute:
            flags.append("+mute")
        if self.mark:
            flags.append("+mark")
        if self.show_if:
            flags.append("+show_if=" + self.show_if)
        if self.hide_if:
            flags.append("+hide_if=" + self.hide_if)

        return self.sharp_engine.statement("#trigger", *arguments,
                flags=flags)

    @property
    def copied(self):
        """Return a copied version of the trigger."""
        copy = Trigger(self.sharp_engine, self.reaction, self.action,
                self.substitution)
        copy.mute = self.mute
        copy.mark = self.mark
        copy.show_if = self.show_if
        copy.hide_if = self.hide_if
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

        reaction = pattern_to_regex(reaction)
        return re.compile(reaction, re.IGNORECASE | re.UNICODE)

    def set_variables(self, match):
        """Set the variables of the trigger in the SharpScript engine.

        This method, to be used internally, put the trigger's variables
        in the SharpEngine locales.  Obviously, this should only be
        used before executing the trigger or asking for the substitution.

        The match can be a string.  In this case, the regular expression
        associated with this trigger is executed and the match is
        created, if the expression matches.

        """
        if isinstance(match, str):
            match = self.re_reaction.search(match)
            if not match:
                return False

        world = self.world
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

        return True

    def replace(self):
        """Return the replacement text if a substitution is set.

        The substsitution is itself a text that can contain variables.
        It is returned, with the variable replaced the same way as
        in SharpScript.  The 'set_variables' must be called before
        calling this method (either directly, or using the 'test'
        method).

        """
        engine = self.sharp_engine
        substitution = engine.replace_variables(self.substitution)
        return substitution.replace("\\{", "{").replace("\\}", "}")

    def is_visible(self):
        """Return whether the triggered line should be displayed.

        A muted trigger is never displayed.  If 'show_if' is set, the
        line is displayed only if this variable exists.  If 'hide_if'
        is set, the line is displayed only if this variable doesn't
        exist.  Variables are checked after the trigger's action
        has run, so the action can change its own visibility.

        """
        if self.mute:
            return False

        variables = self.sharp_engine.locals
        if self.show_if:
            return self.show_if in variables
        if self.hide_if:
            return self.hide_if not in variables

        return True

    def test(self, line, execute=False):
        """Should the trigger be triggered by the text?

        This function return either the matching expression or None.
        If the 'execute' argument is set to True, and the trigger
        should be fired, then call the 'execute' method.

        """
        match = self.re_reaction.search(line)
        if match:
            world = self.world
            world = world and world.name or "unknown"
            if not execute:
                return match

            self.logger.debug("Trigger {}.{} fired.".format(
                    world, repr(self.reaction)))

            # Put the variables in the SharpEngine locales
            self.set_variables(match)

            # Execute the trigger
            self.execute()
            return match

        return None

    def execute(self):
        """Execute the trigger."""
        self.sharp_engine.execute(self.action, variables=True)
