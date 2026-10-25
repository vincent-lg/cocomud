# Copyright (c) 2016-2026, LE GOFF Vincent
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

"""Module containing the Browse function class."""

import wx

from log import logger
from screenreader import ScreenReader
from sharp import Function

# The verbs, in the order of the dialog
VERBS = (
        "next_channel",
        "previous_channel",
        "channel",
        "previous_message",
        "next_message",
        "first_message",
        "last_message",
        "latest",
        "repeat",
        "show",
)

class Browse(Function):

    """Function SharpScript 'browse'.

    It browses the channels of the session without opening a window,
    speaking what it finds.  It's meant for macros:

        #macro {Alt + Right} {#browse next_channel}
        #macro {Alt + Up} {#browse previous_message}
        #macro {Alt + PageUp} {#browse previous_message 10}
        #macro {Alt + 1} {#browse latest 1}
        #macro {Alt + Shift + 2} {#browse channel 2}

    Verbs:
        next_channel, previous_channel    change the channel
        channel <number or name>          go to a channel
        previous_message [n], next_message [n]
                                          move in the channel (1 by default)
        first_message, last_message       go to an end of the channel
        latest <n>                        read the nth latest message
        repeat                            read the current message again
        show                              open the channels dialog there

    Every channel can be browsed, hidden ones too.  The position in
    each channel is shared with the channels dialog.  Before any
    message is read, the current message is the last one.  What's
    spoken interrupts the screen reader, to browse quickly.

    """

    description = "Browse channels"

    def run(self, verb, argument=""):
        """Browse the channels."""
        session = self.sharp_engine.session
        if session is None or self.world is None:
            return

        self.session = session
        method = getattr(self, "verb_" + verb, None)
        if verb not in VERBS or method is None:
            logger("sharp").warning("#browse: unknown verb {!r}".format(
                    verb))
            self.say(self.t("unknown", "Unknown browse action: {verb}.",
                    verb=verb))
            return

        if not self.world.channels:
            self.say(self.t("no_channel", "No channel."))
            return

        method(argument)

    # Helpers
    def say(self, text):
        """Speak the text, interrupting the screen reader."""
        ScreenReader.talk(text, interrupt=True)

    @property
    def channels(self):
        return self.world.channels

    def current(self):
        """Return the index of the current channel."""
        names = [channel.name for channel in self.channels]
        name = self.session.browsing
        return names.index(name) if name in names else 0

    def history(self, index=None):
        """Return the history of a channel (the current one)."""
        if index is None:
            index = self.current()

        return self.session.history(self.channels[index].name)

    def position(self, history):
        """Return the current position, the last message if unset."""
        if history.position is None:
            return len(history.messages) - 1

        return history.position

    def number(self, argument, default):
        try:
            return int(argument)
        except (TypeError, ValueError):
            return default

    def describe(self, index):
        """Go to a channel and say its name and position."""
        self.session.browsing = self.channels[index].name
        history = self.history(index)
        name = self.channels[index].name
        if not history.messages:
            self.say(self.t("empty", "{channel}: empty", channel=name))
        else:
            self.say(self.t("position", "{channel}: {position} of {total}",
                    channel=name, position=self.position(history) + 1,
                    total=len(history.messages)))

    def move(self, step):
        """Move in the current channel and read the message."""
        history = self.history()
        if not history.messages:
            self.say(self.t("empty", "{channel}: empty",
                    channel=history.name))
            return

        last = len(history.messages) - 1
        position = self.position(history) + step
        text = None
        if position < 0:
            position = 0
            text = "top"
        elif position > last:
            position = last
            text = "bottom"

        history.position = position
        message = history.messages[position].text
        if text == "top":
            message = self.t("top", "Top: {message}", message=message)
        elif text == "bottom":
            message = self.t("bottom", "Bottom: {message}", message=message)
        self.say(message)

    # Verbs
    def verb_next_channel(self, argument):
        self.describe((self.current() + 1) % len(self.channels))

    def verb_previous_channel(self, argument):
        self.describe((self.current() - 1) % len(self.channels))

    def verb_channel(self, argument):
        """Go to a channel by number (1 is the first) or by name."""
        argument = argument.strip()
        if argument.isdigit():
            index = int(argument) - 1
            if not 0 <= index < len(self.channels):
                self.say(self.t("no_such_channel",
                        "That channel doesn't exist yet."))
                return
        else:
            names = [channel.name.lower() for channel in self.channels]
            wanted = argument.lower()
            matching = [i for i, name in enumerate(names) if name == wanted]
            matching = matching or [i for i, name in enumerate(names)
                    if name.startswith(wanted)]
            if not wanted or not matching:
                self.say(self.t("unknown_channel",
                        "Unknown channel: {channel}.", channel=argument))
                return
            index = matching[0]

        self.describe(index)

    def verb_previous_message(self, argument):
        self.move(-max(1, self.number(argument, 1)))

    def verb_next_message(self, argument):
        self.move(max(1, self.number(argument, 1)))

    def verb_first_message(self, argument):
        history = self.history()
        self.move(-len(history.messages))

    def verb_last_message(self, argument):
        history = self.history()
        self.move(len(history.messages))

    def verb_latest(self, argument):
        """Read the nth latest message, without moving."""
        history = self.history()
        number = max(1, self.number(argument, 1))
        if number > len(history.messages):
            self.say(self.t("no_message", "No message."))
            return

        self.say(history.messages[-number].text)

    def verb_repeat(self, argument):
        self.move(0)

    def verb_show(self, argument):
        """Open the channels dialog on the current channel and message."""
        from ui.dialogs.channel import ChannelsDialog
        history = self.history()
        dialog = ChannelsDialog(self.engine, self.world, self.session,
                history.name, position=history.position)
        dialog.ShowModal()
        dialog.Destroy()

    # Dialog
    def display(self, dialog, verb="next_channel", argument=""):
        """Display the function's arguments."""
        l_verb = self.t("verb", "Action")
        l_argument = self.t("argument", "Number or channel (optional)")
        labels = [self.t("verb_" + name, name) for name in VERBS]

        l_verb = wx.StaticText(dialog, label=l_verb)
        verbs = wx.Choice(dialog, choices=labels)
        verbs.SetSelection(VERBS.index(verb) if verb in VERBS else 0)
        dialog.verbs = verbs
        dialog.top.Add(l_verb)
        dialog.top.Add(verbs)

        l_argument = wx.StaticText(dialog, label=l_argument)
        t_argument = wx.TextCtrl(dialog, value=argument)
        dialog.argument = t_argument
        dialog.top.Add(l_argument)
        dialog.top.Add(t_argument)

    def complete(self, dialog):
        """The user pressed 'ok' in the dialog."""
        verb = VERBS[max(0, dialog.verbs.GetSelection())]
        argument = dialog.argument.GetValue().strip()
        return (verb, argument) if argument else (verb, )
