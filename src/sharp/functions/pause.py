# Copyright (c) 2023, LE GOFF Vincent
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

"""Module containing the Pause function class."""

from random import uniform
from textwrap import dedent

import wx
from ytranslate import t

from sharp import Function

class Pause(Function):

    """Function SharpScript 'pause'.

    This function expects an argument as a parameter and pauses
    the SharpScript engine.

    """

    description = "Pause the script for a time"

    def display(self, dialog, pause=""):
        """Display the function's argument."""
        try:
            label = t("sharp.pause.time")
        except ValueError:
            label = "Time to pause in seconds"

        l_pause = wx.StaticText(dialog, label=label)
        t_pause = wx.TextCtrl(dialog, value=pause)
        dialog.pause = t_pause
        dialog.top.Add(l_pause)
        dialog.top.Add(t_pause)

    def complete(self, dialog):
        """The user pressed 'ok' in the dialog."""
        pause = dialog.pause.GetValue()
        try:
            empty_pause = t("sharp.pause.empty_time")
        except ValueError:
            empty_pause = "The time to pause is empty."

        if not pause:
            wx.MessageBox(empty_pause, t("ui.alert.error"),
                    wx.OK | wx.ICON_ERROR)
            dialog.pause.SetFocus()
            return None

        return (pause, )

    def custom_code(self, pause=0):
        """Pause the script."""
        if isinstance(pause, str):
            if pause.startswith("'") and pause.endswith("'"):
                pause = pause[1:-1]
            if pause.startswith('"') and pause.endswith('"'):
                pause = pause[1:-1]

            if ".." in pause:
                min_pause, max_pause = pause.split("..", 1)
            else:
                min_pause = max_pause = pause

            try:
                m_pause = float(min_pause)
            except ValueError:
                m_pause = 0

            try:
                x_pause = float(max_pause)
            except ValueError:
                x_pause = 0

            m_pause = m_pause if m_pause > 0 else 0
            x_pause = x_pause if x_pause > 0 else 0

            if m_pause != x_pause:
                pause = uniform(m_pause, x_pause)
            else:
                pause = m_pause

        return f"yield {pause}"
