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

from unittest import TestCase
from unittest.mock import MagicMock, call

from bus import Events, Hooks

class TestHooks(TestCase):

    """Test the hooks, fired by the engine for Python code."""

    def setUp(self):
        self.hooks = Hooks()

    def test_fire(self):
        """Test that a callback receives the fired arguments."""
        callback = MagicMock()
        self.hooks.register("disconnect", callback)
        self.hooks.fire("disconnect", "reason")
        callback.assert_called_once_with("reason")

    def test_other_name(self):
        """Test that a callback isn't called for another hook."""
        callback = MagicMock()
        self.hooks.register("connect", callback)
        self.hooks.fire("disconnect", "reason")
        callback.assert_not_called()

    def test_key(self):
        """Test that a key filters the fired hooks."""
        area = MagicMock()
        every = MagicMock()
        self.hooks.register("msdp", area, key="AREA_NAME")
        self.hooks.register("msdp", every)
        self.hooks.fire("msdp", "HEALTH", "10", key="HEALTH")
        self.hooks.fire("msdp", "AREA_NAME", "Midgaard", key="AREA_NAME")
        area.assert_called_once_with("AREA_NAME", "Midgaard")
        self.assertEqual(every.call_args_list, [call("HEALTH", "10"),
                call("AREA_NAME", "Midgaard")])

    def test_key_prefix(self):
        """Test that a key matches the keys beginning with it and a dot."""
        callback = MagicMock()
        self.hooks.register("gmcp", callback, key="Char")
        for package in ("Char", "Char.Vitals", "Character", "Room"):
            self.hooks.fire("gmcp", package, {}, key=package)

        self.assertEqual(callback.call_args_list, [call("Char", {}),
                call("Char.Vitals", {})])

    def test_key_not_fired(self):
        """Test that a keyed callback ignores a hook fired without key."""
        callback = MagicMock()
        self.hooks.register("msdp", callback, key="HEALTH")
        self.hooks.fire("msdp", "HEALTH", "10")
        callback.assert_not_called()

    def test_unregister(self):
        """Test that an unregistered callback isn't called anymore."""
        callback = MagicMock()
        self.hooks.register("msdp", callback, key="HEALTH")
        self.hooks.unregister("msdp", callback, key="HEALTH")
        self.hooks.fire("msdp", "HEALTH", "10", key="HEALTH")
        callback.assert_not_called()

    def test_unregister_while_firing(self):
        """Test that a callback can unregister itself."""
        def once():
            self.hooks.unregister("connect", once)

        callback = MagicMock()
        self.hooks.register("connect", once)
        self.hooks.register("connect", callback)
        self.hooks.fire("connect")
        self.hooks.fire("connect")
        self.assertEqual(callback.call_count, 2)

    def test_failure(self):
        """Test that a failing callback doesn't stop the others."""
        failing = MagicMock(side_effect=ValueError)
        callback = MagicMock()
        self.hooks.register("connect", failing)
        self.hooks.register("connect", callback)
        self.hooks.logger = MagicMock()
        self.hooks.fire("connect")
        callback.assert_called_once_with()
        self.hooks.logger.exception.assert_called_once()

    def test_result(self):
        """Test that fire returns whether a callback returned True."""
        observer = MagicMock(return_value=None)
        self.hooks.register("line", observer)
        self.assertFalse(self.hooks.fire("line", "Hello"))
        hider = MagicMock(return_value=True)
        self.hooks.register("line", hider)
        self.assertTrue(self.hooks.fire("line", "Hello"))
        self.assertEqual(observer.call_count, 2)


class TestEvents(TestCase):

    """Test the named events, fired for the player."""

    def setUp(self):
        self.events = Events()

    def test_not_handled(self):
        """Test an event without listener."""
        self.assertFalse(self.events.fire("fight", fight_type=3))

    def test_arguments(self):
        """Test that the listeners receive the keyword arguments."""
        listener = MagicMock(return_value=None)
        other = MagicMock()
        self.events.listen("fight", listener)
        self.events.listen("tell", other)
        self.assertFalse(self.events.fire("fight", fight_type=3))
        listener.assert_called_once_with(fight_type=3)
        other.assert_not_called()

    def test_handled(self):
        """Test that a listener returning True handles the event."""
        observer = MagicMock(return_value=None)
        handler = MagicMock(return_value=True)
        self.events.listen("chopvegetables", observer)
        self.events.listen("chopvegetables", handler)
        self.assertTrue(self.events.fire("chopvegetables"))
        observer.assert_called_once_with()

    def test_unlisten(self):
        """Test that a removed listener isn't called anymore."""
        listener = MagicMock(return_value=True)
        self.events.listen("tell", listener)
        self.events.unlisten("tell", listener)
        self.assertFalse(self.events.fire("tell", name="Aelyn"))
        listener.assert_not_called()

    def test_failure(self):
        """Test that a failing listener doesn't handle the event."""
        failing = MagicMock(side_effect=ValueError)
        observer = MagicMock(return_value=None)
        self.events.listen("tell", failing)
        self.events.listen("tell", observer)
        self.events.logger = MagicMock()
        self.assertFalse(self.events.fire("tell"))
        observer.assert_called_once_with()
        self.events.logger.exception.assert_called_once()
