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

"""Module containing the channels dialog."""

import wx

from ytranslate import t

class ChannelsDialog(wx.Dialog):

    """Channels dialog to display channels."""

    def __init__(self, channels, name):
        super(ChannelsDialog, self).__init__(None, title=t("common.channel", 2))
        self.channels = channels
        self.name = name
        self.messages = {}
        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)

        # Create the dialog
        for channel in self.channels:
            label = wx.StaticText(self, label=channel.name)
            messages = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
            messages.InsertColumn(0, t("common.message"))
            i = 0
            for message in channel.messages[:-50]:
                messages.Append((message, ))
                i += 1

            messages.Select(i - 1)
            messages.Focus(i - 1)
            sizer.Add(messages)
            self.messages[channel.name] = messages
            if channel.name == self.name:
                messages.SetFocus()

        # Main sizer
        sizer.Fit(self)
