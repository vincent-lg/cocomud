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

"""Tests of the #event handlers."""

from unittest import TestCase
from unittest.mock import MagicMock

from session import Session
from sharp.engine import SharpScript
from world import MergingMethod, World

class TestEvents(TestCase):

    """Test the #event handlers of a world, run by its sessions."""

    def setUp(self):
        self.world = World("test")
        self.world.engine = MagicMock()
        self.world.sharp_engine = SharpScript(self.world.engine, None,
                self.world)
        self.session = Session(None, self.world)
        self.session.engine = self.world.engine
        self.engine = self.session.sharp_engine

    def add(self, code):
        self.world.sharp_engine.execute(code)

    def test_syntax(self):
        """Test creating and formatting an event handler."""
        self.add("#event chopvegetables {#play sounds/chop.ogg effects}")
        event, = self.world.events
        self.assertEqual(event.key, "chopvegetables")
        self.assertEqual(event.action, "#play sounds/chop.ogg effects")
        self.assertEqual(event.sharp_script,
                "#event chopvegetables {#play sounds/chop.ogg effects}")

    def test_not_handled(self):
        """Test an event without handler."""
        self.assertFalse(self.session.events.fire("fight", fight_type=3))

    def test_variables(self):
        """Test that the arguments become variables of the actions."""
        self.add("#event fight {#writevar seen {type $fight_type}}")
        self.assertTrue(self.session.events.fire("fight", fight_type=3))
        self.assertEqual(self.engine.locals["seen"], "type 3")

    def test_case(self):
        """Test that keys ignore case."""
        self.add("#event Tell {#writevar seen yes}")
        self.assertTrue(self.session.events.fire("tell", name="Aelyn"))
        self.assertFalse(self.session.events.fire("tells"))

    def test_listeners(self):
        """Test that Python listeners and #event handlers both run."""
        listener = MagicMock(return_value=None)
        self.session.events.listen("look", listener)
        self.add("#event look {#writevar seen yes}")
        self.assertTrue(self.session.events.fire("look", sector="forest"))
        listener.assert_called_once_with(sector="forest")
        self.assertEqual(self.engine.locals["seen"], "yes")

    def test_merging(self):
        """Test two handlers for the same key."""
        self.add("#event look {#say one}")
        self.add("#event LOOK {#say two}")
        self.assertEqual([e.action for e in self.world.events], ["#say one"])
        self.world.merging = MergingMethod.replace
        self.add("#event look {#say three}")
        self.assertEqual([e.action for e in self.world.events],
                ["#say three"])

    def test_handler_failure(self):
        """Test that a failing handler doesn't count as handling."""
        events = self.session.events
        events.logger = MagicMock()
        events.handler = MagicMock(side_effect=ValueError)
        self.assertFalse(events.fire("look"))
        events.logger.exception.assert_called_once()
