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

import json
from unittest.mock import MagicMock
import unittest

from protocol.gmcp import GMCP, encode, parse
from version import BUILD

class TestParse(unittest.TestCase):

    """Test the GMCP parser and encoder."""

    def test_with_data(self):
        """Test a message with JSON data."""
        self.assertEqual(parse(b'Char.Vitals {"hp": 100, "maxhp": 120}'),
                ("Char.Vitals", {"hp": 100, "maxhp": 120}))
        self.assertEqual(parse(b'Room.Exits ["n", "s"]'),
                ("Room.Exits", ["n", "s"]))
        self.assertEqual(parse(b'Char.Name "Kredh"'), ("Char.Name", "Kredh"))

    def test_without_data(self):
        """Test a message without data."""
        self.assertEqual(parse(b"Core.Ping"), ("Core.Ping", None))
        self.assertEqual(parse(b"Core.Ping  "), ("Core.Ping", None))

    def test_invalid_json(self):
        """Test data that isn't valid JSON."""
        self.assertEqual(parse(b"Comm.Say hello there"),
                ("Comm.Say", "hello there"))

    def test_utf8(self):
        """Test UTF-8 data."""
        self.assertEqual(parse('Comm.Say "été"'.encode("utf-8")),
                ("Comm.Say", "été"))

    def test_encode(self):
        """Test the encoder."""
        self.assertEqual(encode("Core.Ping"), b"Core.Ping")
        self.assertEqual(parse(encode("Char.Vitals", {"hp": 1})),
                ("Char.Vitals", {"hp": 1}))


class TestOption(unittest.TestCase):

    """Test the GMCP option with a fake client."""

    def setUp(self):
        self.client = MagicMock()
        self.gmcp = GMCP(self.client)

    def sent(self):
        """Return the (package, data) sent through the client."""
        return [parse(call[0][1]) for call in
                self.client.requestNegotiation.call_args_list]

    def test_enable(self):
        """Test the hello and supported packages."""
        self.gmcp.support("Char.Skills 1", "Char 1")
        self.gmcp.enabled = True
        self.gmcp.enable()
        self.assertEqual(self.sent(), [
                ("Core.Hello", {"client": "CocoMUD", "version": str(BUILD)}),
                ("Core.Supports.Set",
                ["Char 1", "Room 1", "Comm 1", "Char.Skills 1"]),
        ])
        self.client.requestNegotiation.assert_called_with(bytes((201, )),
                encode("Core.Supports.Set", self.gmcp.supports))

    def test_support_when_enabled(self):
        """Test adding a supported package when enabled."""
        self.gmcp.enabled = True
        self.gmcp.support("Room 1", "IRE.Rift 1")
        self.assertEqual(self.sent(), [
                ("Core.Supports.Add", ["IRE.Rift 1"])])

    def test_receive(self):
        """Test that listeners receive each message."""
        listener = MagicMock()
        self.gmcp.add_listener(listener)
        self.gmcp.receive(b'Char.Vitals {"hp": 100}')
        listener.assert_called_once_with("Char.Vitals", {"hp": 100})
        self.assertEqual(self.gmcp.packages["Char.Vitals"], {"hp": 100})
