# Copyright (c) 2016-2026, LE GOFF Vincent
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

"""Module containing the Event class."""

from textwrap import dedent

from log import sharp as logger

class Event:

    """An event handler, created with `#event`.

    It runs SharpScript actions when an event is fired: by a world
    script ("chopvegetables", "fight") or by CocoMUD itself ("connect",
    "disconnect", "focus_gained", "focus_lost").  The event's arguments
    become variables of the actions:

        #event tell {#say New tell from $name}

    Keys ignore case.  Running an event handler marks the event as
    handled: a world script then skips its default (a sound, usually).

    """

    def __init__(self, sharp, key, action):
        self.sharp_engine = sharp
        self.key = key
        self.action = dedent(action.strip("\n"))
        self.logger = logger

        # Set the event's level
        self.level = sharp.engine.level

    def __repr__(self):
        return "<Event for {} (level={})>".format(
                repr(self.key), self.level.name)

    @property
    def sharp_script(self):
        """Return the SharpScript code to create this event handler."""
        return self.sharp_engine.format((("#event", self.key,
                self.action), ))

    @property
    def copied(self):
        """Return a copied version of the event handler."""
        copy = Event(self.sharp_engine, self.key, self.action)
        copy.level = self.level
        return copy

    def matches(self, key):
        """Return whether the event handler reacts to this key."""
        return self.key.lower() == key.lower()

    def execute(self, **kwargs):
        """Run the actions, the keyword arguments being variables."""
        self.logger.debug("Event {!r} fired with {!r}.".format(self.key,
                kwargs))
        self.sharp_engine.locals.update(kwargs)
        self.sharp_engine.execute(self.action, variables=True)
