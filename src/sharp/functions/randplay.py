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

"""Module containing the RandPlay function class."""

from pathlib import Path
from random import choice

import wx
from ytranslate import t

from audio import audiolib
from log import logger
from sharp import Function

class RandPlay(Function):

    """Function SharpScript 'randplay'.

    This function plays a random sound from a list.

    """

    description = "Play a sound from a list at random"

    def run(self, filenames):
        """Play the audio file."""
        log = logger("sharp")
        if not filenames:
            return

        filenames = filenames.split(";")
        filename = choice(filenames)
        if self.engine.sounds:
            log.debug(f"#randplay {filename!r}")
        else:
            log.debug(f"#randplay-silent {filename!r}")
            return

        files = self.find_files(filename)
        if files:
            filename = choice(files)
            log.debug(f"#randplay playing {filename!r}")
            audiolib.play(filename)
        else:
            log.warning(f"#randplay cannot find any sound")

    def find_files(self, filename):
        """Return a list of existing files matching this filename."""
        absolute = Path(filename)
        if not absolute.is_absolute():
            absolute = Path(self.world.path) / filename

        # The last part in the file name is searched
        parent = absolute.parent
        match = absolute.parts[-1]
        results = list(parent.rglob(match))
        results = [path for path in results if path.is_file()]
        return [str(path) for path in results]

    def display(self, dialog, filenames=""):
        """Display the function's argument."""
        self.dialog = dialog
        l_files = self.t("files", "Audio files to be played")

        # Dialog
        l_files = wx.StaticText(dialog, label=l_files)
        t_files = wx.TextCtrl(dialog, value=filenames)
        test = wx.Button(dialog, label=t("ui.button.test"))
        dialog.files = t_files
        dialog.top.Add(l_files)
        dialog.top.Add(t_files)
        dialog.top.Add(test)

        # Event binding
        test.Bind(wx.EVT_BUTTON, self.test_files)

    def complete(self, dialog):
        """The user pressed 'ok' in the dialog."""
        files = dialog.files.GetValue()
        empty_path = self.t("empty_path",
                "The path hasn't been set.  What file should I play?")
        if not files:
            wx.MessageBox(empty_path, t("ui.message.error"),
                    wx.OK | wx.ICON_ERROR)
            dialog.files.SetFocus()
            return None

        return (files, )

    def test_files(self, e):
        """Test the audio files."""
        parent = self.dialog
        names = parent.files.GetValue().split(";")
        filename = choice(self.find_files(choice(names)))
        audiolib.play(filename)
