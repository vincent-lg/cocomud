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

"""Base class for Telnet options negotiated with the server.

A Telnet option is identified by a one-byte code.  The server offers
it (IAC WILL <code>), the client accepts (IAC DO <code>), and from then
on both sides can exchange subnegotiations (IAC SB <code> ... IAC SE).
Each supported option is a subclass of `TelnetOption`, which hides
the negotiation and only deals with the payload of subnegotiations.

The client (see 'client.py') creates one instance of each class in
`protocol.OPTIONS` when it is built, and forwards the negotiation
events to it.  The option only needs an object with a
`requestNegotiation(code, payload)` method to send data, which makes
it easy to test without a connection.

"""

from log import logger

class TelnetOption:

    """A Telnet option handled by the client.

    Class attributes to override:
        code: the option code (bytes of length 1).
        name: a short, lowercase name used as a key ('msdp').

    Methods to override:
        enable: called when the option has just been enabled.
        disable: called when the option has been disabled.
        receive: called with the payload of each subnegotiation.

    Listeners are callables added with `add_listener`.  Subclasses
    call `notify` with the arguments they document, and every
    listener is called with them.

    """

    code = None
    name = None

    def __init__(self, client):
        self.client = client
        self.enabled = False
        self.listeners = []
        self.logger = logger("protocol")

    def __repr__(self):
        state = "enabled" if self.enabled else "disabled"
        return "<{} ({})>".format(type(self).__name__, state)

    @property
    def encoding(self):
        """Return the encoding used for the option's strings.

        By default, it's the encoding of the world.

        """
        try:
            return self.client.factory.engine.settings[
                    "options.general.encoding"]
        except Exception:
            return "utf-8"

    def add_listener(self, callback):
        """Add a callback, called when `notify` is called."""
        self.listeners.append(callback)

    def remove_listener(self, callback):
        """Remove a callback previously added."""
        self.listeners.remove(callback)

    def notify(self, *args, **kwargs):
        """Call every listener with the given arguments.

        A failing listener is logged and doesn't prevent the others
        from being called.

        """
        for listener in list(self.listeners):
            try:
                listener(*args, **kwargs)
            except Exception:
                self.logger.exception("A {} listener failed: {!r}".format(
                        self.name, listener))

    def accept(self):
        """Return whether the client accepts the server's offer.

        Override to refuse the option under some conditions (a
        world setting, for instance).

        """
        return True

    def enable(self):
        """The option has just been enabled."""

    def disable(self):
        """The option has just been disabled."""

    def receive(self, payload):
        """Receive the payload of a subnegotiation (bytes)."""

    def send(self, payload):
        """Send a subnegotiation with the given payload (bytes).

        The payload must not be IAC-escaped: Twisted does it.

        """
        if not self.enabled:
            self.logger.warning("Cannot send {}: the option is "
                    "disabled".format(self.name))
            return False

        self.client.requestNegotiation(self.code, payload)
        return True
