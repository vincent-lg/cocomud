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

from unittest.mock import MagicMock

from .models import MockClient
from scripting.alias import Alias

class TestAliases(MockClient):

    """Test aliases."""

    def test_without(self):
        """Test without any aliases."""
        self.client.write(u"some command")
        self.client.transport.write.assert_called_once_with(
                b"some command\r\n")

    def test_simple(self):
        """Test a simple alias without any replacement."""
        alias = Alias(self.client.factory.sharp_engine, "l", "look")
        self.assertEqual(alias.sharp_script, "#alias l look")
        self.client.factory.world.aliases = [alias]
        self.client.write(u"l")
        self.client.transport.write.assert_called_once_with(b"look\r\n")

    def test_variable(self):
        """Test a simple alias with one variable."""
        alias = Alias(self.client.factory.sharp_engine, "s*", "say $1")
        self.assertEqual(alias.sharp_script, "#alias s* {say $1}")
        self.client.factory.world.aliases = [alias]
        self.client.write("l")
        self.client.transport.write.assert_called_once_with(b"l\r\n")
        self.client.transport.write = MagicMock()
        self.client.write("syes!")
        self.client.transport.write.assert_called_once_with(b"say yes!\r\n")

    def test_variable_special(self):
        """Test an alias with one variable containing special characters."""
        alias = Alias(self.client.factory.sharp_engine, "s*", "say $1")
        self.client.factory.world.aliases = [alias]
        self.client.write(u"s\x82lite")
        self.client.transport.write.assert_called_once_with(b"say \x82lite\r\n")

    def test_variables(self):
        """Test a simple alias with several variables."""
        alias = Alias(self.client.factory.sharp_engine,
                "w*=*", "whisper $2 to $1")
        self.assertEqual(alias.sharp_script,
                "#alias w*=* {whisper $2 to $1}")
        self.client.factory.world.aliases = [alias]
        self.client.write(u"wman=good")
        self.client.transport.write.assert_called_once_with(
                b"whisper good to man\r\n")

    def test_sharp(self):
        """Try to send more complex SharpScript through an alias."""
        alias = Alias(self.client.factory.sharp_engine,
                "hp", "#say {HP = 8}")
        self.assertEqual(alias.sharp_script,
                "#alias hp {#say {HP = 8}}")
        self.client.factory.world.aliases = [alias]
        self.client.handle_message = MagicMock()
        self.client.write(u"hp")
        self.client.transport.write.assert_not_called()
        kwargs = {
                "screen": True,
                "speech": True,
                "braille": True,
        }

        self.client.handle_message.assert_called_once_with("HP = 8", **kwargs)
