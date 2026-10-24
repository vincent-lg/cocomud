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

"""GMCP (Generic MUD Communication Protocol), Telnet option 201.

A GMCP message is a package name, optionally followed by a space and
JSON data, encoded in UTF-8:

    Char.Vitals {"hp": 100, "maxhp": 120}
    Core.Ping

Package names are dot-separated and case-insensitive.  When the option
is enabled, the client introduces itself (Core.Hello) and tells the
server which packages it supports (Core.Supports.Set).  The server
only sends messages from the supported packages.

Specification: https://tintin.mudhalla.net/protocols/gmcp/

"""

import json

from protocol.base import TelnetOption
from version import BUILD


def parse(payload):
    """Parse a GMCP payload and return (package, data).

    `data` is the decoded JSON, or None if there's no data.  If the
    data isn't valid JSON, it's returned as a str.

    """
    text = payload.decode("utf-8", errors="replace")
    package, _, data = text.partition(" ")
    data = data.strip()
    if not data:
        return package, None

    try:
        return package, json.loads(data)
    except ValueError:
        return package, data


def encode(package, data=None):
    """Encode a GMCP message and return the payload (bytes)."""
    text = package
    if data is not None:
        text += " " + json.dumps(data)

    return text.encode("utf-8")


class GMCP(TelnetOption):

    """The GMCP Telnet option.

    Listeners are called with (package, data) for each received
    message.  The last data of each package is also kept in
    `packages`.

    Supported packages ("Char 1") can be added before the option is
    enabled: they are sent to the server when it is.

    """

    code = bytes((201, ))
    name = "gmcp"
    encoding = "utf-8"

    def __init__(self, client):
        super().__init__(client)
        self.packages = {}
        self.supports = ["Char 1", "Room 1", "Comm 1"]

    def enable(self):
        """Introduce the client and send the supported packages."""
        self.logger.info("GMCP enabled")
        self.send_message("Core.Hello", {
                "client": "CocoMUD",
                "version": str(BUILD),
        })
        if self.supports:
            self.send_message("Core.Supports.Set", self.supports)

    def disable(self):
        """The option has been disabled."""
        self.logger.info("GMCP disabled")

    def receive(self, payload):
        """Parse the message and notify the listeners."""
        package, data = parse(payload)
        self.logger.debug("Received GMCP {} {!r}".format(package, data))
        self.packages[package] = data
        self.notify(package, data)

    def send_message(self, package, data=None):
        """Send a GMCP message to the server."""
        return self.send(encode(package, data))

    def support(self, *modules):
        """Add supported packages, like 'Char.Skills 1'."""
        added = [module for module in modules if module not in self.supports]
        self.supports.extend(added)
        if added and self.enabled:
            self.send_message("Core.Supports.Add", added)
