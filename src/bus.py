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

"""Hooks and events, the two ways for code to react to the game.

Hooks are fired by the engine and only Python code (world scripts)
listens to them.  They carry raw data, as it was received:

    connect ()               the client has connected
    disconnect (reason)      the client has been disconnected
    focus (focused)          the window gained (True) or lost focus
    msdp (name, value)       an MSDP variable, filtered by name
    gmcp (package, data)     a GMCP message, filtered by package
    line (line)              a received line, without ANSI codes, before
                             the triggers.  A callback returning True
                             hides the line (no display, no trigger)

Events are named and meaningful to the player ("chopvegetables",
"fight").  World scripts fire them, and so does the engine for a few
of them ("connect", "disconnect", "focus").  SharpScript reacts to them
with `#event`, Python can listen to them too.

Each session has its own `hooks` and `events`.  Everything runs in the
reactor's thread, which is also the wx main thread.

"""

from log import logger

class Hooks:

    """The hooks of a session.

    A callback is registered for a hook name, optionally with a key
    to filter what it receives:

    >>> hooks.register("msdp", on_area, key="AREA_NAME")
    >>> hooks.fire("msdp", "AREA_NAME", "Midgaard", key="AREA_NAME")

    A callback registered with a key is called when the fired key is
    the same, or begins with the registered key followed by a dot.
    "Char" therefore matches the GMCP packages "Char" and "Char.Vitals",
    but not "Character".  A callback registered without a key receives
    everything.  The callbacks always receive all the fired arguments.

    """

    def __init__(self):
        self.callbacks = {}
        self.logger = logger("bus")

    def register(self, name, callback, key=None):
        """Register a callback for a hook, optionally filtered by key."""
        self.callbacks.setdefault(name, []).append((key, callback))

    def unregister(self, name, callback, key=None):
        """Remove a callback previously registered."""
        callbacks = self.callbacks.get(name, [])
        callbacks.remove((key, callback))

    def fire(self, name, *args, key=None, **kwargs):
        """Call the callbacks registered for this hook.

        Return whether a callback returned a true value, which only
        some hooks use (the line hook hides the line).  A failing
        callback is logged, doesn't prevent the others from being
        called and doesn't count.

        """
        result = False
        for registered, callback in list(self.callbacks.get(name, ())):
            if registered is not None and not matches(registered, key):
                continue

            try:
                if callback(*args, **kwargs):
                    result = True
            except Exception:
                self.logger.exception("The {} hook failed: {!r}".format(
                        name, callback))

        return result


class Events:

    """The events of a session.

    Listeners are registered for an event key and called with the
    keyword arguments of `fire`:

    >>> events.listen("fight", on_fight)
    >>> events.fire("fight", fight_type=3)
    False

    `fire` returns whether the event has been handled, that is
    whether a listener returned a true value.  It lets the script
    firing an event skip its default behavior (playing a sound, for
    instance) when the player has defined something else.  A listener
    that only observes the event should return None.

    """

    def __init__(self):
        self.listeners = {}
        self.logger = logger("bus")

    def listen(self, key, callback):
        """Add a listener for an event key."""
        self.listeners.setdefault(key, []).append(callback)

    def unlisten(self, key, callback):
        """Remove a listener previously added."""
        self.listeners.get(key, []).remove(callback)

    def fire(self, key, **kwargs):
        """Fire an event, return whether it has been handled.

        A failing listener is logged, doesn't prevent the others from
        being called and doesn't count as handling the event.

        """
        handled = False
        for callback in list(self.listeners.get(key, ())):
            try:
                if callback(**kwargs):
                    handled = True
            except Exception:
                self.logger.exception("The {} event listener failed: "
                        "{!r}".format(key, callback))

        return handled


def matches(registered, key):
    """Return whether a fired key matches a registered key."""
    if key is None:
        return False

    return key == registered or key.startswith(registered + ".")
