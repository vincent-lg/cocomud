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

"""Module containing the Repeat function class."""

import wx
from ytranslate import t

from sharp import Function

class Repeat(Function):

    """Function SharpScript '#repeat'.

    This function can be used to repeat a command, once or several
    times.  It has different syntax:

    Repeat the last command:
        #repeat 1
    Repeat three times the 'look' command:
        #repeat look 3

    """

    description = "Repeat a command X times"

    def run(self, times, command=None):
        """Repeat a command."""
        if not self.client:
            return

        client = self.client
        panel = client.factory.panel
        if not command:
            for last in reversed(panel.extensions["history"].commands[:-1]):
                if not last.startswith("#") or last.startswith("##"):
                    command = last

        times = int(times)
        if command:
            for time in range(times):
                self.client.write(command)

    def display(self, dialog, times="1", command=""):
        """Display the function's arguments."""
        l_times = self.t("times", "Number of times to repeat the command")
        l_command = self.t("command", "Command to repeat (leave blank " \
                "to send the last command in your history")

        # Times
        l_times = wx.StaticText(dialog, label=l_times)
        t_times = wx.TextCtrl(dialog, value=times)
        dialog.times = t_times
        dialog.top.Add(l_times)
        dialog.top.Add(t_times)

        # Command
        l_command = wx.StaticText(dialog, label=l_command)
        t_command = wx.TextCtrl(dialog, value=command)
        dialog.command = t_command
        dialog.top.Add(l_command)
        dialog.top.Add(t_command)


    def complete(self, dialog):
        """The user pressed 'ok' in the dialog."""
        times = dialog.times.GetValue()
        empty_times = self.t("empty_times",
                "You didn't specify the number of times you want " \
                "this command to repeat. Specify 1 at least.")
        invalid_times = self.t("invalid_times",
                "The number of times you specified isn't a valid number.")

        if not times:
            wx.MessageBox(empty_times, t("ui.alert.error"),
                    wx.OK | wx.ICON_ERROR)
            dialog.times.SetFocus()
            return None

        if not times.isdigit():
            wx.MessageBox(invalid_times, t("ui.alert.error"),
                    wx.OK | wx.ICON_ERROR)
            dialog.times.SetFocus()
            return None

        command = dialog.command.GetValue()

        arguments = [times]
        if command:
            arguments.append(command)

        return tuple(arguments)
