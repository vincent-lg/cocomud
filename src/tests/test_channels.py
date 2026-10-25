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

"""Tests of the channels and their history in each session."""

from unittest import TestCase
from unittest.mock import MagicMock

from session import Session
from sharp.engine import SharpScript
from world import World

class TestChannels(TestCase):

    """Test that channels belong to the world, history to sessions."""

    def setUp(self):
        self.world = World("test")
        self.world.engine = MagicMock()
        self.world.sharp_engine = SharpScript(self.world.engine, None,
                self.world)
        self.world.sharp_engine.execute("#channel tells")

    def session(self):
        session = Session(None, self.world)
        session.engine = self.world.engine
        return session

    def test_feed(self):
        """Test feeding a channel in a session."""
        session = self.session()
        session.sharp_engine.execute("#feed tells {Aelyn tells you hi.}")
        history = session.history("tells")
        self.assertEqual([m.text for m in history.messages],
                ["Aelyn tells you hi."])
        self.assertIsNone(history.position)
        self.assertIsInstance(history.messages[0].time, float)

    def test_sessions(self):
        """Test that two sessions on the same world don't share history."""
        first = self.session()
        second = self.session()
        first.sharp_engine.execute("#feed tells one")
        second.sharp_engine.execute("#feed tells two")
        self.assertEqual([m.text for m in first.history("tells").messages],
                ["one"])
        self.assertEqual([m.text for m in second.history("tells").messages],
                ["two"])
        self.assertEqual([c.name for c in self.world.channels], ["tells"])

    def test_unknown_channel(self):
        """Test that feeding a channel the world doesn't have does nothing."""
        session = self.session()
        session.sharp_engine.execute("#feed ooc hello")
        self.assertEqual(session.histories, {})

    def test_world_engine(self):
        """Test that #feed in config.set, without a session, does nothing."""
        self.world.sharp_engine.execute("#feed tells hello")
        self.assertFalse(hasattr(self.world.channels[0], "messages"))

    def test_hidden(self):
        """Test creating a hidden channel and saving it."""
        self.world.sharp_engine.execute("#channel {house chat} -visible")
        tells, house = self.world.channels
        self.assertTrue(tells.visible)
        self.assertFalse(house.visible)
        self.assertEqual(tells.sharp_script, "#channel {tells}")
        self.assertEqual(house.sharp_script, "#channel {house chat} -visible")

    def test_hidden_reload(self):
        """Test that the saved script creates the same channel."""
        self.world.sharp_engine.execute("#channel chat -visible")
        script = self.world.channels[1].sharp_script
        self.world.channels[:] = []
        self.world.sharp_engine.execute(script)
        channel, = self.world.channels
        self.assertEqual(channel.name, "chat")
        self.assertFalse(channel.visible)

    def test_listeners(self):
        """Test that listeners are told about new messages."""
        session = self.session()
        history = session.history("tells")
        listener = MagicMock()
        history.listeners.append(listener)
        session.sharp_engine.execute("#feed tells hello")
        listener.assert_called_once_with(history, history.messages[0])
