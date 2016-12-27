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

"""Module containing the bug dialog."""

import os
import wx

from ytranslate import t

class BugDialog(wx.Dialog):

    """Dialog displayed when a bug occurs."""

    def __init__(self, trace):
        wx.Dialog.__init__(self, None,
                title=t("ui.dialog.bug.title"))
        self.trace = trace
        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Create the dialog
        self.text = wx.TextCtrl(self, size=(600, 400),
                style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.text.SetValue(t("ui.dialog.bug.message",
                traceback=self.trace))
        sizer.Add(self.text)

        # Buttons
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        report = wx.Button(self, label=t("ui.dialog.bug.report"))
        close = wx.Button(self, label=t("ui.button.close"))
        buttons.Add(report)
        buttons.Add(close)
        sizer.Add(buttons)

        # Event binding
        report.Bind(wx.EVT_BUTTON, self.OnReport)
        close.Bind(wx.EVT_BUTTON, self.OnClose)

    def OnReport(self, e):
        """The user clicked on the 'report' button."""
        url = t("ui.dialog.bug.url")
        os.startfile(url)

    def OnClose(self, e):
        """The user clicked on the 'close' button."""
        self.Destroy()
