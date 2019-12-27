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

"""Module containing the Feed function class."""

import wx

from sharp import Function

class Feed(Function):

    """Function SharpScript 'feed'."""

    description = "Feed a channel with a message"

    def run(self, channel, message):
        """Feed a channel."""
        if self.world:
            for t_channel in self.world.channels:
                if t_channel.name == channel:
                    t_channel.feed(message)
                    return

    def display(self, dialog, channel="", message=""):
        """Display the function's argument."""
        l_channel = self.t("channel", "Name of the channel to be fed")
        l_message = self.t("message", "Message to feed to the channel")

        # Channel
        l_channel = wx.StaticText(dialog, label=l_channel)
        t_channel = wx.TextCtrl(dialog, value=channel)
        dialog.channel = t_channel
        dialog.top.Add(l_channel)
        dialog.top.Add(t_channel)

        # Message
        l_message = wx.StaticText(dialog, label=l_message)
        t_message = wx.TextCtrl(dialog, value=message)
        dialog.message = t_message
        dialog.top.Add(l_message)
        dialog.top.Add(t_message)


    def complete(self, dialog):
        """The user pressed 'ok' in the dialog."""
        channel = dialog.channel.GetValue()
        empty_channel = self.t("empty_channel",
                "The channel name is empty.  Where to send the message?")

        if not channel:
            wx.MessageBox(empty_channel, t("ui.message.error"),
                    wx.OK | wx.ICON_ERROR)
            dialog.channel.SetFocus()
            return None

        message = dialog.message.GetValue()
        empty_message = self.t("empty_message",
                "The message is empty.  What to send to the channel?")

        if not message:
            wx.MessageBox(empty_message, t("ui.message.error"),
                    wx.OK | wx.ICON_ERROR)
            dialog.message.SetFocus()
            return None

        arguments = [channel, message]
        return tuple(arguments)
