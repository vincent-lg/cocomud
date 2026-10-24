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

from unittest.mock import MagicMock, call, patch

from twisted.conch.telnet import IAC, DO, DONT, WILL, WONT, SB, SE

from .models import MockClient
from protocol import msdp

MSDP = bytes((69, ))
GMCP = bytes((201, ))

class TestNegotiation(MockClient):

    """Test the Telnet option negotiation, from the received bytes."""

    def setUp(self):
        super().setUp()
        self.client.applicationDataReceived = MagicMock()
        self.msdp = self.client.protocols["msdp"]
        self.gmcp = self.client.protocols["gmcp"]

    def written(self):
        """Return the bytes written to the transport, and reset it."""
        data = b"".join(args[0] for args, _ in
                self.client.transport.write.call_args_list)
        self.client.transport.write.reset_mock()
        return data

    def test_accept(self):
        """Test that MSDP is accepted and reports are sent after DO."""
        self.msdp.report("HEALTH")
        self.client.dataReceived(IAC + WILL + MSDP)
        self.assertTrue(self.msdp.enabled)
        self.assertEqual(self.written(), IAC + DO + MSDP +
                IAC + SB + MSDP + msdp.encode("REPORT", "HEALTH") + IAC + SE)

    def test_gmcp(self):
        """Test that GMCP is accepted and says hello."""
        self.client.dataReceived(IAC + WILL + GMCP)
        self.assertTrue(self.gmcp.enabled)
        written = self.written()
        self.assertTrue(written.startswith(IAC + DO + GMCP +
                IAC + SB + GMCP + b"Core.Hello "))

    def test_refuse_unknown(self):
        """Test that an unknown option is refused."""
        self.client.dataReceived(IAC + WILL + bytes((99, )))
        self.assertEqual(self.written(), IAC + DONT + bytes((99, )))

    def test_refuse_by_option(self):
        """Test an option refusing the server's offer."""
        self.msdp.accept = MagicMock(return_value=False)
        self.client.dataReceived(IAC + WILL + MSDP)
        self.assertFalse(self.msdp.enabled)
        self.assertEqual(self.written(), IAC + DONT + MSDP)

    def test_will_twice(self):
        """Test that a repeated WILL doesn't enable the option twice."""
        self.msdp.enable = MagicMock()
        self.client.dataReceived(IAC + WILL + MSDP)
        self.client.dataReceived(IAC + WILL + MSDP)
        self.msdp.enable.assert_called_once_with()

    def test_receive(self):
        """Test a subnegotiation surrounded by text."""
        listener = MagicMock()
        self.msdp.add_listener(listener)
        self.client.dataReceived(IAC + WILL + MSDP)
        payload = msdp.encode("ROOM_NAME", "A forest")
        self.client.dataReceived(b"before" + IAC + SB + MSDP + payload +
                IAC + SE + b"after")
        listener.assert_called_once_with("ROOM_NAME", "A forest")
        self.assertEqual(self.client.applicationDataReceived.call_args_list,
                [call(b"before"), call(b"after")])

    def test_receive_split(self):
        """Test a subnegotiation received in several chunks."""
        listener = MagicMock()
        self.msdp.add_listener(listener)
        self.client.dataReceived(IAC + WILL + MSDP)
        data = IAC + SB + MSDP + msdp.encode("MONEY", "12") + IAC + SE
        for i in range(len(data)):
            self.client.dataReceived(data[i:i + 1])
        listener.assert_called_once_with("MONEY", "12")

    def test_receive_escaped_iac(self):
        """Test a payload containing an escaped IAC (byte 255)."""
        listener = MagicMock()
        self.msdp.add_listener(listener)
        self.client.dataReceived(IAC + WILL + MSDP)
        self.client.dataReceived(IAC + SB + MSDP + bytes((msdp.VAR, )) +
                b"SAY" + bytes((msdp.VAL, )) + b"\xff\xff" + IAC + SE)
        listener.assert_called_once_with("SAY", "\xff")

    def test_failing_option(self):
        """Test that a failing option doesn't break the connection."""
        self.client.dataReceived(IAC + WILL + MSDP)
        self.msdp.receive = MagicMock(side_effect=RuntimeError)
        self.client.dataReceived(IAC + SB + MSDP + b"x" + IAC + SE + b"ok")
        self.client.applicationDataReceived.assert_called_once_with(b"ok")

    def test_wont(self):
        """Test that the server can disable an option."""
        self.client.dataReceived(IAC + WILL + MSDP)
        self.written()
        self.client.dataReceived(IAC + WONT + MSDP)
        self.assertFalse(self.msdp.enabled)
        self.assertEqual(self.written(), IAC + DONT + MSDP)
        self.assertFalse(self.msdp.send_variable("SEND", "ROOM"))

    def test_connection_lost(self):
        """Test that options are disabled when the connection is lost."""
        self.client.dataReceived(IAC + WILL + MSDP)
        self.msdp.disable = MagicMock()
        self.client.send_queue = MagicMock()
        with patch("client.wx"):
            self.client.connectionLost(MagicMock())
        self.assertFalse(self.msdp.enabled)
        self.msdp.disable.assert_called_once_with()
