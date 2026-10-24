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

from unittest.mock import MagicMock
import unittest

from protocol.msdp import (
        MSDP, MSDPError, encode, parse,
        VAR, VAL, TABLE_OPEN, TABLE_CLOSE, ARRAY_OPEN, ARRAY_CLOSE)

def packet(*parts):
    """Build a payload from special bytes (int) and strings (str)."""
    data = b""
    for part in parts:
        if isinstance(part, int):
            data += bytes((part, ))
        else:
            data += part.encode("utf-8")

    return data


class TestParse(unittest.TestCase):

    """Test the MSDP parser."""

    def test_simple(self):
        """Test a single string variable."""
        data = packet(VAR, "MONEY", VAL, "374246")
        self.assertEqual(parse(data), {"MONEY": "374246"})

    def test_several(self):
        """Test several variables in one payload, in order."""
        data = packet(VAR, "HEALTH", VAL, "10", VAR, "MANA", VAL, "20")
        variables = parse(data)
        self.assertEqual(variables, {"HEALTH": "10", "MANA": "20"})
        self.assertEqual(list(variables), ["HEALTH", "MANA"])

    def test_empty(self):
        """Test empty values, with or without VAL."""
        self.assertEqual(parse(packet(VAR, "TELL", VAL)), {"TELL": ""})
        self.assertEqual(parse(packet(VAR, "TELL")), {"TELL": ""})
        self.assertEqual(parse(b""), {})

    def test_array(self):
        """Test an array."""
        data = packet(VAR, "EXITS", VAL, ARRAY_OPEN, VAL, "north", VAL,
                "south", ARRAY_CLOSE)
        self.assertEqual(parse(data), {"EXITS": ["north", "south"]})

    def test_multiple_values(self):
        """Test several VAL after one VAR, read as an array."""
        data = packet(VAR, "REPORT", VAL, "HEALTH", VAL, "MANA")
        self.assertEqual(parse(data), {"REPORT": ["HEALTH", "MANA"]})

    def test_table(self):
        """Test a table."""
        data = packet(VAR, "ROOM", VAL, TABLE_OPEN, VAR, "VNUM", VAL,
                "6008", VAR, "NAME", VAL, "The forest", TABLE_CLOSE)
        self.assertEqual(parse(data), {"ROOM": {
                "VNUM": "6008", "NAME": "The forest"}})

    def test_nested(self):
        """Test tables in a table, and arrays of tables."""
        data = packet(VAR, "ROOM", VAL, TABLE_OPEN,
                VAR, "EXITS", VAL, TABLE_OPEN,
                    VAR, "n", VAL, "6011", VAR, "e", VAL, "6007",
                TABLE_CLOSE,
                VAR, "MOBS", VAL, ARRAY_OPEN,
                    VAL, TABLE_OPEN, VAR, "NAME", VAL, "a rat", TABLE_CLOSE,
                    VAL, ARRAY_OPEN, ARRAY_CLOSE,
                ARRAY_CLOSE,
                TABLE_CLOSE, VAR, "AFTER", VAL, "1")
        self.assertEqual(parse(data), {
            "ROOM": {
                "EXITS": {"n": "6011", "e": "6007"},
                "MOBS": [{"NAME": "a rat"}, []],
            },
            "AFTER": "1",
        })

    def test_unclosed(self):
        """Test a table or array not closed at the end."""
        data = packet(VAR, "EXITS", VAL, ARRAY_OPEN, VAL, "north")
        self.assertEqual(parse(data), {"EXITS": ["north"]})
        data = packet(VAR, "ROOM", VAL, TABLE_OPEN, VAR, "VNUM", VAL, "1")
        self.assertEqual(parse(data), {"ROOM": {"VNUM": "1"}})

    def test_malformed(self):
        """Test malformed payloads."""
        with self.assertRaises(MSDPError):
            parse(b"MONEY")
        with self.assertRaises(MSDPError):
            parse(packet(VAR, "A", VAL, TABLE_CLOSE))
        with self.assertRaises(MSDPError):
            parse(packet(VAR, "A", VAL, ARRAY_OPEN, VAR, "B", ARRAY_CLOSE))

    def test_encoding(self):
        """Test strings decoded with the given encoding."""
        data = bytes((VAR, )) + b"SAY" + bytes((VAL, )) + "été".encode(
                "latin-1")
        self.assertEqual(parse(data, "latin-1"), {"SAY": "été"})


class TestEncode(unittest.TestCase):

    """Test the MSDP encoder."""

    def test_simple(self):
        """Test a string and a number."""
        self.assertEqual(encode("REPORT", "HEALTH"),
                packet(VAR, "REPORT", VAL, "HEALTH"))
        self.assertEqual(encode("LEVEL", 5), packet(VAR, "LEVEL", VAL, "5"))

    def test_array_and_table(self):
        """Test an array and a table."""
        self.assertEqual(encode("A", ["x", "y"]),
                packet(VAR, "A", VAL, ARRAY_OPEN, VAL, "x", VAL, "y",
                ARRAY_CLOSE))
        self.assertEqual(encode("T", {"k": "v"}),
                packet(VAR, "T", VAL, TABLE_OPEN, VAR, "k", VAL, "v",
                TABLE_CLOSE))

    def test_round_trip(self):
        """Test that parsing an encoded value gives it back."""
        value = {"EXITS": {"n": "1"}, "MOBS": [{"NAME": "rat"}, "x"]}
        self.assertEqual(parse(encode("ROOM", value)), {"ROOM": value})

    def test_special(self):
        """Test strings containing a special byte."""
        with self.assertRaises(MSDPError):
            encode("REPORT", "HEAL\x01TH")


class TestOption(unittest.TestCase):

    """Test the MSDP option with a fake client."""

    def setUp(self):
        self.client = MagicMock()
        self.client.factory.engine.settings = {
                "options.general.encoding": "utf-8"}
        self.msdp = MSDP(self.client)

    def sent(self):
        """Return the payloads sent through the client."""
        return [call[0][1] for call in
                self.client.requestNegotiation.call_args_list]

    def test_receive(self):
        """Test that listeners receive each variable."""
        listener = MagicMock()
        self.msdp.add_listener(listener)
        self.msdp.receive(packet(VAR, "HEALTH", VAL, "10", VAR, "MANA",
                VAL, "20"))
        self.assertEqual(listener.call_args_list, [
                (("HEALTH", "10"), ), (("MANA", "20"), )])
        self.assertEqual(self.msdp.variables["MANA"], "20")

    def test_failing_listener(self):
        """Test that a failing listener doesn't stop the others."""
        listener = MagicMock()
        self.msdp.add_listener(MagicMock(side_effect=RuntimeError))
        self.msdp.add_listener(listener)
        self.msdp.receive(packet(VAR, "HEALTH", VAL, "10"))
        listener.assert_called_once_with("HEALTH", "10")

    def test_receive_malformed(self):
        """Test that a malformed payload is ignored."""
        listener = MagicMock()
        self.msdp.add_listener(listener)
        self.msdp.receive(b"garbage")
        listener.assert_not_called()

    def test_report_before_enabled(self):
        """Test that reports are sent once the option is enabled."""
        self.msdp.report("HEALTH", "MANA", "HEALTH")
        self.assertEqual(self.sent(), [])
        self.msdp.enabled = True
        self.msdp.enable()
        self.assertEqual(self.sent(), [
                encode("REPORT", "HEALTH"), encode("REPORT", "MANA")])
        self.client.requestNegotiation.assert_called_with(
                bytes((69, )), encode("REPORT", "MANA"))

    def test_report_when_enabled(self):
        """Test reports and other commands when enabled."""
        self.msdp.enabled = True
        self.msdp.report("HEALTH")
        self.msdp.unreport("HEALTH")
        self.msdp.unreport("UNKNOWN")
        self.msdp.request("ROOM")
        self.msdp.list("REPORTABLE_VARIABLES")
        self.assertEqual(self.sent(), [
                encode("REPORT", "HEALTH"),
                encode("UNREPORT", "HEALTH"),
                encode("SEND", "ROOM"),
                encode("LIST", "REPORTABLE_VARIABLES"),
        ])

    def test_send_disabled(self):
        """Test that nothing is sent when the option is disabled."""
        self.assertFalse(self.msdp.send_variable("SEND", "ROOM"))
        self.client.requestNegotiation.assert_not_called()
