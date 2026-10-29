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

from .models import MockClient
from scripting.alias import Alias
from scripting.trigger import Trigger

class TestTriggers(MockClient):

    """Test the visibility of triggered lines."""

    def setUp(self):
        super().setUp()
        self.client.factory.panel = None
        self.client.factory.strip_ansi = True
        self.client.factory.session.hooks.fire = MagicMock(
                return_value=False)
        self.client.handle_message = MagicMock()

    def add_trigger(self, reaction, action="", substitution="", **flags):
        """Create a trigger and make it the only one of the world."""
        trigger = Trigger(self.client.factory.sharp_engine, reaction,
                action, substitution)
        for name, value in flags.items():
            setattr(trigger, name, value)

        self.client.factory.world.triggers = [trigger]
        return trigger

    def displayed(self, text="before\r\nHP: 50\r\nafter"):
        """Send lines to the client and return what was displayed."""
        self.client.handle_message.reset_mock()
        self.client.handle_lines(text)
        return self.client.handle_message.call_args[0][0]

    def test_sharp_flags(self):
        """Test that flags with a value are converted to keywords."""
        sharp = self.client.factory.sharp_engine
        code = sharp.convert_to_python(
                ("#trigger", "{HP: *}", "{}", "+show_if=show_hp", "+mark"))
        self.assertEqual(code,
                "trigger('HP: *', '', show_if='show_hp', mark=True)")

    def test_sharp_script(self):
        """Test that the conditions are written back in SharpScript."""
        trigger = self.add_trigger("HP: *", substitution="Health: $1",
                show_if="show_hp")
        self.assertEqual(trigger.sharp_script,
                "#trigger {HP: *} {} {Health: $1} +show_if=show_hp")
        trigger = self.add_trigger("HP: *", hide_if="quiet")
        self.assertEqual(trigger.sharp_script,
                "#trigger {HP: *} {} +hide_if=quiet")
        copy = trigger.copied
        self.assertEqual((copy.show_if, copy.hide_if), ("", "quiet"))

    def test_mute(self):
        """A muted trigger hides its line, substitution included."""
        self.add_trigger("HP: *", substitution="Health: $1", mute=True)
        self.assertEqual(self.displayed(), "before\r\nafter")

    def test_show_if(self):
        """The line is visible only when the variable exists."""
        sharp = self.client.factory.sharp_engine
        self.add_trigger("HP: *", show_if="show_hp")
        self.assertEqual(self.displayed(), "before\r\nafter")
        sharp.locals["show_hp"] = "1"
        self.assertEqual(self.displayed(), "before\r\nHP: 50\r\nafter")

    def test_hide_if(self):
        """The line is hidden as long as the variable exists."""
        sharp = self.client.factory.sharp_engine
        self.add_trigger("HP: *", hide_if="quiet")
        self.assertEqual(self.displayed(), "before\r\nHP: 50\r\nafter")
        sharp.locals["quiet"] = "1"
        self.assertEqual(self.displayed(), "before\r\nafter")

    def test_condition_with_substitution(self):
        """A visible line is replaced, a hidden one shows nothing."""
        sharp = self.client.factory.sharp_engine
        self.add_trigger("HP: *", substitution="Health: $1",
                show_if="show_hp")
        self.assertEqual(self.displayed(), "before\r\nafter")
        sharp.locals["show_hp"] = "1"
        self.assertEqual(self.displayed(), "before\r\nHealth: 50\r\nafter")

    def test_toggle_with_alias(self):
        """Aliases using #writevar switch the line on and off."""
        world = self.client.factory.world
        sharp = self.client.factory.sharp_engine
        self.add_trigger("HP: *", hide_if="quiet")
        world.aliases = [
                Alias(sharp, "quiet", "#writevar quiet {1}"),
                Alias(sharp, "noisy", "#writevar quiet {}"),
        ]
        self.client.write("quiet")
        self.assertEqual(self.displayed(), "before\r\nafter")
        self.client.write("noisy")
        self.assertEqual(self.displayed(), "before\r\nHP: 50\r\nafter")

    def test_action_sets_variable(self):
        """The trigger's own action can change its visibility."""
        self.add_trigger("HP: *", action="#writevar show_hp {$1}",
                show_if="show_hp")
        self.assertEqual(self.displayed(), "before\r\nHP: 50\r\nafter")
