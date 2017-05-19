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

from mock import MagicMock
import unittest

from client import Client
from sharp.engine import SharpScript

class MockClient(unittest.TestCase):

    """A mock client to test client features without side-effects."""

    def setUp(self):
        """Create a real client with some mocking."""
        self.client = Client()
        self.client.transport = MagicMock()
        peer = MagicMock()
        peer.host = "127.0.0.1"
        peer.port = 4000
        self.client.transport.getPeer = MagicMock(return_value=peer)
        self.client.factory = MagicMock()

        # Create the sharp engine
        sharp = SharpScript(self.client.factory.engine, self.client,
                MagicMock())
        sharp.bind_client(self.client)
        self.client.factory.sharp_engine = sharp

        def get_setting(address):
            """Private function to return a set of default settings."""
            default = {
                    "options.input.command_stacking": "",
                    "options.general.encoding": "utf-8",
            }
            return default[address]

        self.client.factory.engine.settings.__getitem__ = MagicMock(
                side_effect=get_setting)
