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

"""Module containing the channels dialog."""

import wx

from ytranslate import t

from scripting.channel import Channel

class ChannelsDialog(wx.Dialog):

    """Channels dialog to display channels."""

    def __init__(self, engine, world, channels, name=None):
        super(ChannelsDialog, self).__init__(None, title=t("common.channel", 2))
        self.engine = engine
        self.world = world
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
            for message in channel.messages[-50:]:
                messages.Append((message, ))
                i += 1

            messages.Select(i - 1)
            messages.Focus(i - 1)
            sizer.Add(messages)
            self.messages[channel.name] = messages
            if channel.name == self.name:
                messages.SetFocus()

        # Buttons
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        add = wx.Button(self, label=t("ui.button.add"))
        buttons.Add(add)
        remove = wx.Button(self, label=t("ui.button.remove"))
        buttons.Add(remove)
        help = wx.Button(self, label=t("ui.button.help"))
        buttons.Add(help)
        sizer.Add(buttons)

        # Main sizer
        sizer.Fit(self)

        # Event binding
        add.Bind(wx.EVT_BUTTON, self.OnAdd)
        remove.Bind(wx.EVT_BUTTON, self.OnRemove)
        help.Bind(wx.EVT_BUTTON, self.OnHelp)

    def OnAdd(self, e):
        """Add a new channel."""
        dialog = wx.TextEntryDialog(self, t("ui.message.channels.name"), t("ui.message.channels.title"))
        dialog.ShowModal()
        name = dialog.GetValue()
        dialog.Destroy()

        # If the name is already used
        if name in [ch.name for ch in self.world.channels]:
            wx.MessageBox(t("ui.message.channels.already"),
                    t("ui.alert.error"), wx.OK | wx.ICON_ERROR)
        else:
            channel = Channel(self.world, name)
            self.world.add_channel(channel)
            self.world.save_config()
            self.Destroy()

    def OnRemove(self, e):
        """ Remove a channel."""
        names = sorted([ch.name for ch in self.world.channels])
        dialog = wx.SingleChoiceDialog(self, t("ui.message.channels.remove"), "", choices=names)
        dialog.ShowModal()
        name = dialog.GetStringSelection()
        dialog.Destroy()

        # If the name is already used
        if name not in [ch.name for ch in self.world.channels]:
            wx.MessageBox(t("ui.message.channels.unknown"),
                    t("ui.alert.error"), wx.OK | wx.ICON_ERROR)
        else:
            self.world.channels[:] = [ch for ch in self.world.channels if ch.name != name]
            self.world.save_config()
            self.Destroy()

    def OnHelp(self, e):
        """The user clicked on 'help'."""
        self.engine.open_help("Channels")
