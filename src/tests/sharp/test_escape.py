# Copyright (c) 2016-2020, LE GOFF Vincent
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

from scripting.alias import Alias
from scripting.trigger import Trigger
from sharp.engine import SharpScript

class TestEscape(unittest.TestCase):

    """Unittest for the escaping of special characters."""

    def setUp(self):
        """Create the SharpScript instance."""
        self.engine = SharpScript(MagicMock(), None, None)
        self.created = []
        self.engine.globals["trigger"] = lambda *args, **kwargs: \
                self.created.append((args, kwargs))

    def reload(self, trigger):
        """Save the trigger in SharpScript and read it back."""
        self.created.clear()
        self.engine.execute(trigger.sharp_script)
        return self.created[0]

    def assertRoundTrip(self, reaction, action="#send {hi}",
            substitution=""):
        """Check that the trigger is read back unchanged."""
        trigger = Trigger(self.engine, reaction, action, substitution)
        trigger.mute = True
        args, kwargs = self.reload(trigger)
        expected = (reaction, action, substitution) if substitution \
                else (reaction, action)
        self.assertEqual(args, expected, trigger.sharp_script)
        self.assertEqual(kwargs, {"mute": True})

    def test_plus_and_minus(self):
        """A leading '+' or '-' isn't read as a flag or Python code."""
        self.assertRoundTrip("+100 experience points.")
        self.assertRoundTrip("+100")
        self.assertRoundTrip("+mute")
        self.assertRoundTrip("-5")
        self.assertRoundTrip("-5 hp")
        trigger = Trigger(self.engine, "+100 experience points.", "")
        self.assertEqual(trigger.sharp_script,
                "#trigger {\\+100 experience points.} {}")

    def test_braces(self):
        """Braces in a value are kept."""
        self.assertRoundTrip("{red}")
        self.assertRoundTrip("{red} ball")
        self.assertRoundTrip("{red ball}")
        self.assertRoundTrip("{+x} y")
        self.assertRoundTrip("{a b")

    def test_unbalanced_braces(self):
        """Unbalanced braces are escaped but still match."""
        trigger = Trigger(self.engine, "a { b", "", "Sub {")
        args, _ = self.reload(trigger)
        self.assertEqual(args[0], "a \\{ b")
        loaded = Trigger(self.engine, *args)
        self.assertTrue(loaded.test("a { b"))
        self.assertEqual(loaded.replace(), "Sub {")

    def test_semicolons(self):
        """Semi-colons are kept, in reactions and actions."""
        self.assertRoundTrip("hi; bye")
        self.assertRoundTrip("hi;bye")
        self.assertRoundTrip("ok", "#send {say a;;b}")
        self.assertRoundTrip("ok", "#play a.wav;#stop")

    def test_others(self):
        """Other values are read back unchanged."""
        self.assertRoundTrip("##x")
        self.assertRoundTrip("x=1")
        self.assertRoundTrip("\\*\\*\\* Welcome *")
        self.assertRoundTrip("\\+x")
        self.assertRoundTrip("ok", "{+\nprint('x')\n}")
        self.assertRoundTrip("ok", "#trigger {\\+1 xp} {#stop}")

    def test_old_python_reaction(self):
        """A reaction saved as '{+...}' by older versions is restored."""
        function = self.engine.functions["trigger"]
        function.world = world = MagicMock()
        self.engine.globals["trigger"] = function.run
        self.engine.execute("#trigger {+100 xp} {}")
        trigger = world.add_trigger.call_args[0][0]
        self.assertEqual(trigger.reaction, "+100 xp")

    def test_escaped_flag(self):
        """An escaped '+' or '-' is an argument, not a flag."""
        self.assertEqual(self.engine.feed("#say \\+speech -braille"),
                ["say('+speech', braille=False)"])
        self.assertEqual(self.engine.feed("#say {\\+1 xp}"),
                ["say('+1 xp')"])

    def test_pattern(self):
        """A backslash makes the next character literal in patterns."""
        trigger = Trigger(self.engine, "\\*\\*\\* Welcome *", "")
        self.assertTrue(trigger.test("*** Welcome home"))
        self.assertFalse(trigger.test("xxx Welcome home"))
        trigger = Trigger(self.engine, "\\^x", "")
        self.assertTrue(trigger.test("^x"))
        trigger = Trigger(self.engine, "a\\\\b", "")
        self.assertTrue(trigger.test("a\\b"))
        trigger = Trigger(self.engine, "+100 *", "")
        self.assertTrue(trigger.test("+100 xp"))
        alias = Alias(self.engine, "\\*star *", "")
        self.assertTrue(alias.re_alias.search("*star north"))
        self.assertFalse(alias.re_alias.search("Xstar north"))
