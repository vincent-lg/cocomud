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

"""Module containing the Play function class."""

import os

from pygame import mixer
import wx
from ytranslate import t

from sharp import Function

mixer.init(buffer=1024)

class Play(Function):

    """Function SharpScript 'play'.

    This function play a sound or music using the Pygame mixer.

    """

    description = "Play an audio file"

    def run(self, filename):
        """Play the audio file."""
        logger = None
        if self.engine:
            logger = self.engine.loggers["cocomud.sharp"]
            logger.debug("#play {}".format(filename))

        filename = self.find_abs_filename(filename)
        if os.path.exists(filename):
            if logger:
                logger.debug("#play playing {}".format(filename))
        else:
            if logger:
                logger.warning("#play cannot find the file at {}".format(
                    filename))

        sound = mixer.Sound(filename)
        sound.play()

    def find_abs_filename(self, filename):
        """Return the absolute path of the file.

        The initial file name can be absolute, or relative to the
        world's location.

        """
        if os.path.isabs(filename):
            pass
        elif os.path.normpath(filename).split(os.path.sep)[0] == "worlds":
            filename = os.path.abspath(filename)
        else:
            path = os.path.join(self.world.path, filename)
            filename = os.path.abspath(path)

        return filename

    def find_rel_filename(self, filename):
        """Return the filename relative to the world's location."""
        location = os.path.abspath(self.world.path)
        return os.path.relpath(filename, location)

    def display(self, dialog, filename=""):
        """Display the function's argument."""
        self.dialog = dialog
        directory = os.path.join(self.world.path, "sounds")
        if not os.path.isdir(directory):
            directory = self.world.path

        dialog.default_directory = directory
        dialog.default_file = filename
        l_file = self.t("file", "Audio file to be played")

        # Dialog
        l_file = wx.StaticText(dialog, label=l_file)
        t_file = wx.TextCtrl(dialog, value=filename)
        browse = wx.Button(dialog, label=t("ui.button.browse"))
        test = wx.Button(dialog, label=t("ui.button.test"))
        dialog.file = t_file
        dialog.top.Add(l_file)
        dialog.top.Add(t_file)
        dialog.top.Add(browse)
        dialog.top.Add(test)

        # Event binding
        browse.Bind(wx.EVT_BUTTON, self.browse_file)
        test.Bind(wx.EVT_BUTTON, self.test_file)

    def complete(self, dialog):
        """The user pressed 'ok' in the dialog."""
        file = dialog.default_file
        empty_path = self.t("empty_path",
                "The path hasn't been set.  What file should I play?")
        if not file:
            wx.MessageBox(empty_path, t("ui.message.error"),
                    wx.OK | wx.ICON_ERROR)
            dialog.file.SetFocus()
            return None

        return (file, )

    def browse_file(self, e):
        """Browse for a file."""
        parent = self.dialog
        extensions = "Audio file (*.wav)|*.wav"
        dialog = wx.FileDialog(parent, t("ui.dialog.choose_file"),
                parent.default_directory, "", extensions,
                wx.OPEN)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            filename = self.find_rel_filename(dialog.GetPath())
            parent.file.SetValue(filename)
            parent.default_file = filename

    def test_file(self, e):
        """Test the audio file."""
        parent = self.dialog
        filename = self.find_abs_filename(parent.default_file)
        sound = mixer.Sound(filename)
        sound.play()
