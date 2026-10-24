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

"""MSDP (Mud Server Data Protocol), Telnet option 69.

MSDP sends variables between the server and the client.  A variable
has a name and a value, and a value is either a string, an array of
values or a table (a mapping of names to values).  Each part is
introduced by a special byte:

    VAR (1) name VAL (2) value
    VAL TABLE_OPEN (3) VAR name VAL value ... TABLE_CLOSE (4)
    VAL ARRAY_OPEN (5) VAL value VAL value ... ARRAY_CLOSE (6)

Several values after the same VAR are read as an array.  Everything is
sent as text: numbers are strings, like '374246'.

The client asks the server to send variables with commands, which are
variables too.  The most useful one is REPORT: the server then sends
the variable whenever its value changes.

    VAR "REPORT" VAL "HEALTH"
    VAR "LIST" VAL "REPORTABLE_VARIABLES"
    VAR "SEND" VAL "ROOM_NAME"

Specification: https://tintin.mudhalla.net/protocols/msdp/

"""

from protocol.base import TelnetOption

# Special bytes
VAR = 1
VAL = 2
TABLE_OPEN = 3
TABLE_CLOSE = 4
ARRAY_OPEN = 5
ARRAY_CLOSE = 6
SPECIAL = bytes((0, VAR, VAL, TABLE_OPEN, TABLE_CLOSE, ARRAY_OPEN,
        ARRAY_CLOSE))

# Bytes that end a string value
END_OF_STRING = (VAR, VAL, TABLE_CLOSE, ARRAY_CLOSE)


class MSDPError(ValueError):

    """An MSDP payload couldn't be parsed or encoded."""


def parse(payload, encoding="utf-8"):
    """Parse an MSDP payload and return a dictionary of variables.

    Args:
        payload: the subnegotiation data, without IAC SB MSDP and
                IAC SE (bytes).
        encoding: the encoding used to decode the strings.

    Returns:
        A dictionary {name: value}, in the order the variables were
        sent.  A value is a str, a list or a dict.

    Raises:
        MSDPError if the payload is malformed.

    """
    parser = _Parser(payload, encoding)
    return parser.read_variables(stop=None)


def encode(name, value, encoding="utf-8"):
    """Encode a variable and return the payload (bytes).

    Args:
        name: the variable name (str).
        value: a str, an int, a float, a list/tuple of values or
                a dict of {name: value}.
        encoding: the encoding used to encode the strings.

    Raises:
        MSDPError if a string contains a special byte.

    """
    return bytes((VAR, )) + _encode_string(name, encoding) + \
            _encode_value(value, encoding)


def _encode_string(text, encoding):
    """Encode a single string."""
    data = str(text).encode(encoding, errors="replace")
    if any(byte in SPECIAL for byte in data):
        raise MSDPError("{!r} contains a special MSDP byte".format(text))

    return data


def _encode_value(value, encoding):
    """Encode a value, including the VAL byte(s) before it."""
    if isinstance(value, dict):
        data = bytes((VAL, TABLE_OPEN))
        for name, sub in value.items():
            data += bytes((VAR, )) + _encode_string(name, encoding)
            data += _encode_value(sub, encoding)
        return data + bytes((TABLE_CLOSE, ))
    elif isinstance(value, (list, tuple)):
        data = bytes((VAL, ARRAY_OPEN))
        for sub in value:
            data += _encode_value(sub, encoding)
        return data + bytes((ARRAY_CLOSE, ))

    return bytes((VAL, )) + _encode_string(value, encoding)


class _Parser:

    """Read an MSDP payload, keeping the current position."""

    def __init__(self, payload, encoding):
        self.payload = payload
        self.encoding = encoding
        self.pos = 0

    @property
    def current(self):
        """Return the current byte, or None at the end."""
        if self.pos < len(self.payload):
            return self.payload[self.pos]

        return None

    def read_variables(self, stop):
        """Read VAR name VAL value pairs until `stop` or the end."""
        variables = {}
        while self.current is not None and self.current != stop:
            if self.current != VAR:
                raise MSDPError("expected VAR at {}, got {}".format(
                        self.pos, self.current))

            self.pos += 1
            name = self.read_string()
            values = []
            while self.current == VAL:
                self.pos += 1
                values.append(self.read_value())

            if not values:
                value = ""
            elif len(values) == 1:
                value = values[0]
            else:
                value = values
            variables[name] = value

        return variables

    def read_value(self):
        """Read a value after VAL: a string, a table or an array."""
        if self.current == TABLE_OPEN:
            self.pos += 1
            value = self.read_variables(stop=TABLE_CLOSE)
            self.close(TABLE_CLOSE)
        elif self.current == ARRAY_OPEN:
            self.pos += 1
            value = []
            while self.current is not None and self.current != ARRAY_CLOSE:
                if self.current != VAL:
                    raise MSDPError("expected VAL at {}, got {}".format(
                            self.pos, self.current))

                self.pos += 1
                value.append(self.read_value())
            self.close(ARRAY_CLOSE)
        else:
            value = self.read_string()

        return value

    def read_string(self):
        """Read a string until a special byte or the end."""
        start = self.pos
        while self.current is not None and \
                self.current not in END_OF_STRING:
            self.pos += 1

        data = self.payload[start:self.pos]
        return data.decode(self.encoding, errors="replace")

    def close(self, byte):
        """Skip a closing byte.

        A missing closing byte at the end of the payload is tolerated.

        """
        if self.current == byte:
            self.pos += 1
        elif self.current is not None:
            raise MSDPError("expected {} at {}, got {}".format(
                    byte, self.pos, self.current))


class MSDP(TelnetOption):

    """The MSDP Telnet option.

    Listeners are called with (name, value) for each received
    variable.  The last value of each variable is also kept in
    `variables`.

    Variables to report can be requested before the option is
    enabled: they are sent to the server when it is.

    """

    code = bytes((69, ))
    name = "msdp"

    def __init__(self, client):
        super().__init__(client)
        self.variables = {}
        self.reports = []

    def enable(self):
        """Send the REPORT commands requested so far."""
        self.logger.info("MSDP enabled")
        for name in self.reports:
            self.send_variable("REPORT", name)

    def disable(self):
        """The option has been disabled."""
        self.logger.info("MSDP disabled")

    def receive(self, payload):
        """Parse the variables and notify the listeners."""
        try:
            variables = parse(payload, self.encoding)
        except MSDPError as err:
            self.logger.warning("Cannot parse MSDP {!r}: {}".format(
                    payload, err))
            return

        for name, value in variables.items():
            self.logger.debug("Received MSDP {}={!r}".format(name, value))
            self.variables[name] = value
            self.notify(name, value)

    def send_variable(self, name, value):
        """Send a variable to the server."""
        return self.send(encode(name, value, self.encoding))

    def report(self, *names):
        """Ask the server to report these variables when they change.

        Each variable is sent in its own packet, as the Erion
        soundpack does.

        """
        for name in names:
            if name not in self.reports:
                self.reports.append(name)
                if self.enabled:
                    self.send_variable("REPORT", name)

    def unreport(self, *names):
        """Ask the server to stop reporting these variables."""
        for name in names:
            if name in self.reports:
                self.reports.remove(name)
                if self.enabled:
                    self.send_variable("UNREPORT", name)

    def request(self, *names):
        """Ask the server to send the current value of these variables."""
        for name in names:
            self.send_variable("SEND", name)

    def list(self, what):
        """Ask the server for a list, like 'REPORTABLE_VARIABLES'."""
        return self.send_variable("LIST", what)
