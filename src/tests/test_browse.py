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

"""Tests of the #browse function."""

from unittest import TestCase
from unittest.mock import MagicMock, patch

from session import Session
from sharp.engine import SharpScript
from world import World

class TestBrowse(TestCase):

    """Test browsing channels with #browse."""

    def setUp(self):
        self.world = World("test")
        self.world.engine = MagicMock()
        self.world.sharp_engine = SharpScript(self.world.engine, None,
                self.world)
        self.world.sharp_engine.execute(
                "#channel all\n#channel tells\n#channel exits -visible")
        self.session = Session(None, self.world)
        self.session.engine = self.world.engine
        for i in range(1, 6):
            self.session.history("all").feed("message {}".format(i))
        self.session.history("exits").feed("[Exits: north]")
        patcher = patch("sharp.functions.browse.ScreenReader.talk")
        self.talk = patcher.start()
        self.addCleanup(patcher.stop)

    def browse(self, code):
        """Run #browse, return what was said."""
        self.talk.reset_mock()
        self.session.sharp_engine.execute("#browse " + code)
        return [args[0] for args, kwargs in self.talk.call_args_list]

    def test_channels(self):
        """Test changing channels, hidden ones included."""
        self.assertEqual(self.browse("next_channel"), ["tells: empty"])
        self.assertEqual(self.browse("next_channel"), ["exits: 1 of 1"])
        self.assertEqual(self.browse("next_channel"), ["all: 5 of 5"])
        self.assertEqual(self.browse("previous_channel"), ["exits: 1 of 1"])
        self.talk.assert_called_once_with("exits: 1 of 1", interrupt=True)

    def test_messages(self):
        """Test moving in a channel, from the last message."""
        self.assertEqual(self.browse("previous_message"), ["message 4"])
        self.assertEqual(self.browse("previous_message 10"),
                ["Top: message 1"])
        self.assertEqual(self.browse("next_message"), ["message 2"])
        self.assertEqual(self.browse("last_message"), ["Bottom: message 5"])
        self.assertEqual(self.browse("first_message"), ["Top: message 1"])
        self.assertEqual(self.browse("repeat"), ["message 1"])
        self.assertEqual(self.session.history("all").position, 0)

    def test_latest(self):
        """Test reading the latest messages without moving."""
        self.browse("first_message")
        self.assertEqual(self.browse("latest 1"), ["message 5"])
        self.assertEqual(self.browse("latest 3"), ["message 3"])
        self.assertEqual(self.browse("latest 9"), ["No message."])
        self.assertEqual(self.session.history("all").position, 0)

    def test_channel(self):
        """Test going to a channel by number or name."""
        self.assertEqual(self.browse("channel 3"), ["exits: 1 of 1"])
        self.assertEqual(self.browse("channel 9"),
                ["That channel doesn't exist yet."])
        self.assertEqual(self.browse("channel Tells"), ["tells: empty"])
        self.assertEqual(self.browse("channel ex"), ["exits: 1 of 1"])
        self.assertEqual(self.browse("channel ooc"),
                ["Unknown channel: ooc."])
        self.assertEqual(self.browse("previous_message"),
                ["Top: [Exits: north]"])

    def test_empty(self):
        """Test reading an empty channel."""
        self.browse("channel tells")
        self.assertEqual(self.browse("previous_message"), ["tells: empty"])
        self.assertEqual(self.browse("latest 1"), ["No message."])

    def test_sessions(self):
        """Test that each session has its own current channel."""
        other = Session(None, self.world)
        other.engine = self.world.engine
        other.history("all").feed("other message")
        self.browse("channel tells")
        self.talk.reset_mock()
        other.sharp_engine.execute("#browse repeat")
        self.talk.assert_called_once_with("other message", interrupt=True)
        self.assertEqual(self.session.browsing, "tells")
        self.assertIsNone(other.browsing)

    def test_unknown(self):
        """Test an unknown verb and a world without channels."""
        self.assertEqual(self.browse("dance"),
                ["Unknown browse action: dance."])
        self.world.channels[:] = []
        self.assertEqual(self.browse("next_channel"), ["No channel."])
