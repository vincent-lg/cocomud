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

"""Module containing the task dialog."""

from ytranslate import t
import wx
from wx.lib.pubsub import pub

from screenreader import ScreenReader

class TaskDialog(wx.Dialog):

    """A dialog for asynchronous tasks.

    This dialog is meant for tasks (see the 'task' package) visible
    in the foreground.  This dialog has a progress bar and a message.
    This dialog is created by the task and displays a progress
    indicator regarding the task completion.  The dialog is generally
    destroyed after the task is complete.

    The dialog provides the following methods that triggers events:
        UpdateTitle(title): change the dialog's title.
        UpdateProgress(number): change the progress bar percentage.
        UpdateText(text): change the displayed text.

    """

    def __init__(self, task, title):
        wx.Dialog.__init__(self, None, title=title)
        self.task = task
        self.message = ""
        self.confirmation = "Are you sure you want to cancel this task?"
        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Create the dialog
        self.text = wx.TextCtrl(self, value=self.message,
                size=(600, 100), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.gauge = wx.Gauge(self, range=100, size=(250, 25))
        self.cancel = wx.Button(self, wx.ID_CANCEL)

        # Window design
        sizer.Add(self.text)
        sizer.Add(self.gauge)
        sizer.Add(self.cancel)

        # Event binding
        pub.subscribe(self.OnUpdateProgress, "UpdateProgress")
        pub.subscribe(self.OnUpdateText, "UpdateText")
        pub.subscribe(self.OnUpdateTitle, "UpdateTitle")
        self.Bind(wx.EVT_BUTTON, self.OnCancel, self.cancel)

    def OnUpdateProgress(self, value=0):
        """Update the progress level."""
        if self:
            text = self.text.GetValue()
            ScreenReader.talk("{}% {}".format(value, text), speech=False)
            self.gauge.SetValue(value)

    def OnUpdateText(self, text):
        """Update thetext."""
        if self:
            self.text.SetValue(text)

    def OnUpdateTitle(self, title):
        """Update the title."""
        if self:
            self.SetTitle(title)

    def OnCancel(self, e):
        """The user clicks on 'cancel'."""
        value = wx.MessageBox(self.confirmation, t("ui.alert.confirm"),
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        if value == wx.YES:
            self.task.cancelled = True
            self.Destroy()

    def UpdateProgress(self, value):
        """Change the level indicator."""
        wx.CallAfter(pub.sendMessage, "UpdateProgress", value=value)

    def UpdateText(self, text):
        """Change the text."""
        wx.CallAfter(pub.sendMessage, "UpdateText", text=text)

    def UpdateTitle(self, title):
        """Change the text."""
        wx.CallAfter(pub.sendMessage, "UpdateTitle", title=title)
