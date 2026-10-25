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

"""Tests of the #play and #randplay functions."""

import os
import shutil
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch

from sharp.engine import SharpScript
from sharp.functions.play import Play
from sharp.functions.randplay import RandPlay

class TestPlay(TestCase):

    """Test playing sounds, with or without a category."""

    def setUp(self):
        self.directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.directory, ignore_errors=True)
        os.makedirs(os.path.join(self.directory, "sounds"))
        for name in ("crash.ogg", "hit1.ogg"):
            with open(os.path.join(self.directory, "sounds", name), "wb"):
                pass

        self.engine = MagicMock()
        self.engine.sounds = True
        self.world = MagicMock()
        self.world.path = self.directory
        patcher = patch("audio.audiolib.play")
        self.play = patcher.start()
        self.addCleanup(patcher.stop)

    def path(self, name):
        return os.path.abspath(os.path.join(self.directory, "sounds", name))

    def test_syntax(self):
        """Test that the category is a second argument."""
        engine = SharpScript(None, None, None)
        self.assertEqual(engine.feed("#play sounds/crash.ogg effects"),
                ["play('sounds/crash.ogg', 'effects')"])

    def test_play(self):
        """Test #play without a category."""
        Play(self.engine, None, None, self.world).run("sounds/crash.ogg")
        self.play.assert_called_once_with(self.path("crash.ogg"),
                category=None)

    def test_play_category(self):
        """Test #play in a category."""
        Play(self.engine, None, None, self.world).run("sounds/crash.ogg",
                "effects")
        self.play.assert_called_once_with(self.path("crash.ogg"),
                category="effects")

    def test_randplay_category(self):
        """Test #randplay in a category."""
        RandPlay(self.engine, None, None, self.world).run("sounds/hit*.ogg",
                "combat")
        self.play.assert_called_once_with(self.path("hit1.ogg"),
                category="combat")

    def test_silent(self):
        """Test that nothing plays when sounds are off."""
        self.engine.sounds = False
        Play(self.engine, None, None, self.world).run("sounds/crash.ogg",
                "effects")
        self.play.assert_not_called()
