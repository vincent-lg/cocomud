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

import os
import shutil
import tempfile
from textwrap import dedent
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from client import Client
from scripts import ScriptAudio
from session import Session

class TestScripts(TestCase):

    """Test the loading of world scripts and their API."""

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.directory, ignore_errors=True)
        self.world = MagicMock()
        self.world.path = self.directory
        self.session = Session(None, self.world)
        self.session.scripts.logger = MagicMock()

    def write(self, filename, code):
        """Write a script in the world's scripts folder."""
        folder = os.path.join(self.directory, "scripts")
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, filename), "w",
                encoding="utf-8") as file:
            file.write(dedent(code))

    def load(self):
        """Load the scripts, fail on errors."""
        errors = self.session.scripts.load(self.world)
        self.assertEqual(errors, [])

    def test_no_folder(self):
        """Test a world without scripts."""
        self.load()
        self.assertTrue(self.session.scripts.loaded)
        self.assertEqual(self.session.scripts.modules, {})

    def test_order(self):
        """Test that scripts are loaded in alphabetical order."""
        self.write("b.py", "session.order.append('b')")
        self.write("a.py", "session.order.append('a')")
        self.write("notes.txt", "not Python")
        self.session.order = []
        self.load()
        self.assertEqual(self.session.order, ["a", "b"])
        self.assertEqual(sorted(self.session.scripts.modules), ["a", "b"])

    def test_hook(self):
        """Test the hook decorator."""
        self.write("music.py", """
            areas = []

            @hook("msdp", "AREA_NAME")
            def area_changed(name, value):
                areas.append(value)
        """)
        self.load()
        hooks = self.session.hooks
        hooks.fire("msdp", "HEALTH", "10", key="HEALTH")
        hooks.fire("msdp", "AREA_NAME", "Midgaard", key="AREA_NAME")
        module = self.session.scripts.modules["music"]
        self.assertEqual(module.areas, ["Midgaard"])
        self.assertEqual(self.session.msdp_reports, ["AREA_NAME"])

    def test_events(self):
        """Test firing and listening to events."""
        self.write("sounds.py", """
            fights = []

            @events.listen("fight")
            def on_fight(fight_type):
                fights.append(fight_type)
                return True

            @hook("msdp", "FIGHT")
            def fight(name, value):
                global handled
                handled = events.fire("fight", fight_type=int(value))
        """)
        self.load()
        self.session.hooks.fire("msdp", "FIGHT", "3", key="FIGHT")
        module = self.session.scripts.modules["sounds"]
        self.assertEqual(module.fights, [3])
        self.assertTrue(module.handled)

    def test_error(self):
        """Test that a failing script doesn't stop the others."""
        self.write("a.py", "1 / 0")
        self.write("b.py", "loaded = True")
        errors = self.session.scripts.load(self.world)
        self.assertEqual([filename for filename, _ in errors], ["a.py"])
        self.assertIn("ZeroDivisionError", errors[0][1])
        self.assertTrue(self.session.scripts.modules["b"].loaded)

    def test_unload(self):
        """Test that unloading removes the hooks and listeners."""
        self.write("a.py", """
            calls = []

            @hook("connect")
            def connected():
                calls.append("hook")

            @events.listen("connect")
            def on_connect():
                calls.append("event")
        """)
        self.load()
        module = self.session.scripts.modules["a"]
        self.session.scripts.unload()
        self.session.hooks.fire("connect")
        self.session.events.fire("connect")
        self.assertEqual(module.calls, [])
        self.assertFalse(self.session.scripts.loaded)

    def test_reload(self):
        """Test that reloading doesn't duplicate the hooks."""
        self.write("a.py", """
            @hook("connect")
            def connected():
                session.calls += 1
        """)
        self.session.calls = 0
        self.load()
        self.assertEqual(self.session.scripts.reload(self.world), [])
        self.session.hooks.fire("connect")
        self.assertEqual(self.session.calls, 1)

    def test_command(self):
        """Test a command and its arguments."""
        self.write("commands.py", """
            calls = []

            @command("sound")
            def sound(args):
                calls.append(("sound", args))

            @command("sound  Volume")
            def volume(args):
                calls.append(("volume", args))
        """)
        self.load()
        scripts = self.session.scripts
        self.assertTrue(scripts.run_command("sound"))
        self.assertTrue(scripts.run_command("Sound VOLUME  Music 50 "))
        self.assertTrue(scripts.run_command("sound volumes"))
        self.assertFalse(scripts.run_command("soundtrack"))
        self.assertFalse(scripts.run_command(""))
        self.assertEqual(scripts.modules["commands"].calls, [
                ("sound", ""), ("volume", "Music 50"),
                ("sound", "volumes")])

    def test_command_error(self):
        """Test that a failing command is logged and consumed."""
        self.write("a.py", """
            @command("boom")
            def boom(args):
                1 / 0
        """)
        self.load()
        self.assertTrue(self.session.scripts.run_command("boom now"))
        self.session.scripts.logger.exception.assert_called_once()

    def test_command_unload(self):
        """Test that unloading removes the commands."""
        self.write("a.py", """
            @command("sound")
            def sound(args):
                pass
        """)
        self.load()
        self.session.scripts.unload()
        self.assertFalse(self.session.scripts.run_command("sound"))

    def test_send(self):
        """Test sending commands, line by line, without aliases."""
        self.write("a.py", """
            @hook("connect")
            def connected():
                send("look\\nscore")
        """)
        self.load()
        self.session.client = MagicMock()
        self.session.hooks.fire("connect")
        self.assertEqual(self.session.client.write.call_args_list,
                [call("look", alias=False), call("score", alias=False)])

    def test_send_disconnected(self):
        """Test that sending without client only logs a warning."""
        self.write("a.py", "send('look')")
        self.load()
        self.session.scripts.logger.warning.assert_called_once()

    def test_reports_kept(self):
        """Test that each new client receives the reports and supports."""
        self.write("a.py", """
            @hook("msdp", "ROOM_NAME")
            def room(name, value):
                pass

            msdp.report("HEALTH", "ROOM_NAME")
            gmcp.support("Char 1")
        """)
        self.load()
        for _ in range(2):
            client = Client()
            self.session.bind_client(client)
            self.assertEqual(client.protocols["msdp"].reports,
                    ["ROOM_NAME", "HEALTH"])
            self.assertIn("Char 1", client.protocols["gmcp"].supports)

    def test_report_connected(self):
        """Test reports asked while a client is bound."""
        client = Client()
        self.session.bind_client(client)
        self.write("a.py", """
            msdp.report("MONEY", "HEALTH")
            msdp.unreport("MONEY")
        """)
        self.load()
        self.assertEqual(client.protocols["msdp"].reports, ["HEALTH"])
        self.assertEqual(self.session.msdp_reports, ["HEALTH"])

    def test_protocol_disconnected(self):
        """Test that other protocol calls need a client."""
        self.write("a.py", """
            def request():
                msdp.request("HEALTH")
        """)
        self.load()
        with self.assertRaises(RuntimeError):
            self.session.scripts.modules["a"].request()


class TestScriptAudio(TestCase):

    """Test the audio library given to scripts."""

    def setUp(self):
        self.world = MagicMock()
        self.world.path = os.path.abspath("worlds/erion")
        self.audio = ScriptAudio(self.world)
        self.library = MagicMock()
        patcher = patch.object(ScriptAudio, "library", self.library)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_play(self):
        """Test that relative paths are relative to the world."""
        self.audio.play("sounds/hit.ogg", category="combat")
        path = os.path.join(self.world.path, "sounds", "hit.ogg")
        self.library.play.assert_called_once_with(path, category="combat")

    def test_absolute(self):
        """Test that absolute paths are kept."""
        path = os.path.abspath("elsewhere/hit.ogg")
        self.audio.play(path)
        self.library.play.assert_called_once_with(path)

    def test_channel(self):
        """Test that channels resolve relative paths too."""
        channel = self.audio.channel("music", category="music")
        channel.play("music/area.ogg", loop=True)
        path = os.path.join(self.world.path, "music", "area.ogg")
        self.library.channel.return_value.play.assert_called_once_with(
                path, loop=True)
        channel.volume = 50
        self.assertEqual(self.library.channel.return_value.volume, 50)

    def test_library(self):
        """Test that other attributes are the library's."""
        self.audio.stop(category="music")
        self.library.stop.assert_called_once_with(category="music")
