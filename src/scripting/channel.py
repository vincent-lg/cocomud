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

"""Module containing the Channel, History and Message classes."""

import time

from log import logger

class Channel:

    """A channel object.

    A channel keeps track of messages of a kind, typically channel
    messages.  They can be fed with triggers.  For instance, if an
    'ooc' message is received, then a channel can be fed to keep track
    of all 'ooc' messages.  This makes browsing through history a lot
    easier.

    The channel must first be created through the #channel SharpScript
    action.  A world can have several channels, identified by a unique
    name.  To feed a channel, one should use the #feed action.

    The channel belongs to the world, but its messages belong to each
    session (see `History`): two characters connected to the same game
    share channels, not their history.

    A hidden channel (`#channel name -visible`) isn't listed in the
    channels dialog, unless it's opened by name.  A channel created by
    a world script isn't saved in config.set (`saved` is False): the
    script creates it again each time.

    """

    def __init__(self, world, name, visible=True, saved=True):
        self.world = world
        self.name = name
        self.visible = visible
        self.saved = saved

    def __repr__(self):
        return "<Channel {} for {}>".format(
                repr(self.name), self.world and self.world.name or "unknown")

    @property
    def sharp_script(self):
        """Return the SharpScript code to create this channel."""
        script = "#channel {{{}}}".format(self.name)
        if not self.visible:
            script += " -visible"

        return script


class History:

    """The messages of a channel in a session.

    The position is the index of the message being read, or None
    if no message has been read yet.  Listeners are called with the
    history and the new message each time a message is added (the
    channels dialog uses it to show new messages).

    """

    def __init__(self, name):
        self.name = name
        self.messages = []
        self.position = None
        self.listeners = []

    def __repr__(self):
        return "<History of {} ({} messages)>".format(repr(self.name),
                len(self.messages))

    def feed(self, text):
        """Append a message at the end of the history."""
        message = Message(text)
        self.messages.append(message)
        for listener in list(self.listeners):
            listener(self, message)

        return message


class Message:

    """A message in a channel history, with the time it was received."""

    def __init__(self, text, received=None):
        self.text = text
        self.time = time.time() if received is None else received

    def __repr__(self):
        return "<Message {}>".format(repr(self.text))
