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

"""Module containing the Send function class."""

from textwrap import dedent

import wx
from ytranslate import t

from sharp import Function

class Send(Function):

    """Function SharpScript 'send'.

    This function expects an argument as a parameter and sends it
    to the client and the server behind it.

    """

    description = "Send a message"

    def run(self, text):
        """Send the text."""
        text = dedent(text.strip("\n"))
        if self.client:
            for line in text.splitlines():
                line = line.encode("latin-1")
                self.client.write(line)

    def display(self, dialog, commands=""):
        """Display the function's argument."""
        try:
            label = t("sharp.send.command")
        except ValueError:
            label = "Commands to be sent"

        l_commands = wx.StaticText(dialog, label=label)
        t_commands = wx.TextCtrl(dialog, value=commands,
                style=wx.TE_MULTILINE)
        dialog.commands = t_commands
        dialog.top.Add(l_commands)
        dialog.top.Add(t_commands)

    def complete(self, dialog):
        """The user pressed 'ok' in the dialog."""
        commands = dialog.commands.GetValue().encode("utf-8", "replace")
        try:
            empty_commands = t("sharp.send.empty_commands")
        except ValueError:
            empty_commands = "The commands field is empty."

        if not commands:
            wx.MessageBox(empty_commands, t("ui.message.error"),
                    wx.OK | wx.ICON_ERROR)
            dialog.commands.SetFocus()
            return None

        return (commands, )
