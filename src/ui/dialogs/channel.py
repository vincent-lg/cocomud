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

import time

import wx

from ytranslate import t

from screenreader import ScreenReader
from scripting.channel import Channel

class ChannelsDialog(wx.Dialog):

    """Channels dialog, showing one channel at a time.

    The channel list contains the visible channels (and the channel
    asked for, even if hidden).  The messages of the selected channel
    come from the session's history, and new messages are added while
    the dialog is open.  Opening the dialog on a channel selects its
    last message, unless `position` is set.  Changing the channel
    (Ctrl+Tab, Ctrl+Shift+Tab or the list) selects the message at the
    channel's position.  Selecting a message moves the history's
    position, shared with browsing.

    """

    def __init__(self, engine, world, session, name=None, position=None):
        super(ChannelsDialog, self).__init__(None,
                title=t("common.channel", 2))
        self.engine = engine
        self.world = world
        self.session = session
        self.name = name
        self.position = position
        self.listening = None

        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Channel list
        l_channels = wx.StaticText(self,
                label=t("ui.message.channels.channel"))
        self.choices = wx.Choice(self)
        sizer.Add(l_channels)
        sizer.Add(self.choices)

        # Messages of the selected channel
        l_messages = wx.StaticText(self,
                label=t("ui.message.channels.messages"))
        self.messages = wx.ListCtrl(self, size=(600, 300),
                style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.messages.InsertColumn(0, t("common.message"), width=450)
        self.messages.InsertColumn(1, t("ui.message.channels.time"),
                width=130)
        sizer.Add(l_messages)
        sizer.Add(self.messages, proportion=1, flag=wx.EXPAND)

        # Buttons
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        add = wx.Button(self, label=t("ui.button.add"))
        buttons.Add(add)
        remove = wx.Button(self, label=t("ui.button.remove"))
        buttons.Add(remove)
        help = wx.Button(self, label=t("ui.button.help"))
        buttons.Add(help)
        close = wx.Button(self, wx.ID_CLOSE)
        buttons.Add(close)
        self.SetEscapeId(wx.ID_CLOSE)
        sizer.Add(buttons)
        sizer.Fit(self)

        # Event binding
        self.Bind(wx.EVT_CHAR_HOOK, self.OnCharHook)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.choices.Bind(wx.EVT_CHOICE, self.OnChannel)
        self.messages.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnMessage)
        add.Bind(wx.EVT_BUTTON, self.OnAdd)
        remove.Bind(wx.EVT_BUTTON, self.OnRemove)
        help.Bind(wx.EVT_BUTTON, self.OnHelp)
        close.Bind(wx.EVT_BUTTON, self.OnClose)

        self.populate_channels(self.name)
        if self.messages.GetItemCount():
            self.messages.SetFocus()
        else:
            self.choices.SetFocus()

    @property
    def channel(self):
        """Return the selected channel, or None."""
        index = self.choices.GetSelection()
        if 0 <= index < len(self.channels):
            return self.channels[index]

        return None

    def history(self, channel):
        """Return the session's history of a channel, or None."""
        if self.session is None or channel is None:
            return None

        return self.session.history(channel.name)

    def populate_channels(self, name=None):
        """Fill the channel list, selecting a channel by name."""
        self.channels = [channel for channel in self.world.channels
                if channel.visible or channel.name == name]
        self.choices.Set([channel.name for channel in self.channels])
        names = [channel.name for channel in self.channels]
        index = names.index(name) if name in names else 0
        if self.channels:
            self.choices.SetSelection(index)
        self.populate_messages(self.position)

    def populate_messages(self, position=None):
        """Fill the message list of the selected channel.

        The message at `position` is selected, or the last one.

        """
        self.messages.DeleteAllItems()
        history = self.history(self.channel)
        self.listen(history)
        if history is None or not history.messages:
            return

        for message in history.messages:
            self.messages.Append((message.text, format_time(message.time)))

        last = len(history.messages) - 1
        if position is None or not 0 <= position <= last:
            position = last
        self.messages.Select(position)
        self.messages.Focus(position)
        self.messages.EnsureVisible(position)

    def listen(self, history):
        """Show the new messages of this history only."""
        if self.listening is not None:
            self.listening.listeners.remove(self.new_message)

        self.listening = history
        if history is not None:
            history.listeners.append(self.new_message)

    def new_message(self, history, message):
        """A message was added to the displayed channel."""
        try:
            self.messages.Append((message.text, format_time(message.time)))
        except RuntimeError:
            # The dialog was destroyed without being closed
            history.listeners.remove(self.new_message)
            return

        if self.messages.GetItemCount() == 1:
            self.messages.Select(0)
            self.messages.Focus(0)

    def switch(self, step):
        """Select the next (1) or previous (-1) channel."""
        if not self.channels:
            return

        index = (self.choices.GetSelection() + step) % len(self.channels)
        self.choices.SetSelection(index)
        # The channel list shows the name on a Braille display already
        ScreenReader.talk(self.channels[index].name, braille=False)
        self.show_channel()

    def show_channel(self):
        """Show the selected channel at its position."""
        history = self.history(self.channel)
        self.populate_messages(history and history.position)
        if self.messages.GetItemCount():
            self.messages.SetFocus()

    def OnCharHook(self, e):
        """Ctrl+Tab and Ctrl+Shift+Tab change the channel."""
        if e.GetKeyCode() == wx.WXK_TAB and e.ControlDown():
            self.switch(-1 if e.ShiftDown() else 1)
        else:
            e.Skip()

    def OnChannel(self, e):
        """Another channel is selected in the list."""
        history = self.history(self.channel)
        self.populate_messages(history and history.position)

    def OnMessage(self, e):
        """A message is selected: move the history's position."""
        history = self.history(self.channel)
        if history is not None:
            history.position = e.GetIndex()

    def OnAdd(self, e):
        """Add a new channel."""
        dialog = wx.TextEntryDialog(self, t("ui.message.channels.name"),
                t("ui.message.channels.title"))
        dialog.ShowModal()
        name = dialog.GetValue().strip()
        dialog.Destroy()
        if not name:
            return

        # If the name is already used
        if name in [ch.name for ch in self.world.channels]:
            wx.MessageBox(t("ui.message.channels.already"),
                    t("ui.alert.error"), wx.OK | wx.ICON_ERROR)
        else:
            channel = Channel(self.world, name)
            self.world.add_channel(channel)
            self.world.save_config()
            self.populate_channels(name)
            self.choices.SetFocus()

    def OnRemove(self, e):
        """Remove a channel."""
        names = sorted([ch.name for ch in self.world.channels])
        dialog = wx.SingleChoiceDialog(self, t("ui.message.channels.remove"),
                "", choices=names)
        result = dialog.ShowModal()
        name = dialog.GetStringSelection()
        dialog.Destroy()
        if result != wx.ID_OK:
            return

        # If the name is unknown
        if name not in [ch.name for ch in self.world.channels]:
            wx.MessageBox(t("ui.message.channels.unknown"),
                    t("ui.alert.error"), wx.OK | wx.ICON_ERROR)
        else:
            self.world.channels[:] = [ch for ch in self.world.channels
                    if ch.name != name]
            self.world.save_config()
            self.populate_channels()
            self.choices.SetFocus()

    def OnHelp(self, e):
        """The user clicked on 'help'."""
        self.engine.open_help("Channels")

    def OnClose(self, e):
        """Close the dialog."""
        self.listen(None)
        self.EndModal(wx.ID_CLOSE)


def format_time(received):
    """Return the time of a message: the hour today, else the date too."""
    when = time.localtime(received)
    if time.strftime("%Y-%m-%d", when) == time.strftime("%Y-%m-%d"):
        return time.strftime("%H:%M:%S", when)

    return time.strftime("%Y-%m-%d %H:%M", when)
