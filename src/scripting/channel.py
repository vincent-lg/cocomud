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

    """

    def __init__(self, world, name):
        self.world = world
        self.name = name

    def __repr__(self):
        return "<Channel {} for {}>".format(
                repr(self.name), self.world and self.world.name or "unknown")


class History:

    """The messages of a channel in a session.

    The position is the index of the message being read, or None
    if no message has been read yet.

    """

    def __init__(self, name):
        self.name = name
        self.messages = []
        self.position = None

    def __repr__(self):
        return "<History of {} ({} messages)>".format(repr(self.name),
                len(self.messages))

    def feed(self, text):
        """Append a message at the end of the history."""
        message = Message(text)
        self.messages.append(message)
        return message


class Message:

    """A message in a channel history, with the time it was received."""

    def __init__(self, text, received=None):
        self.text = text
        self.time = time.time() if received is None else received

    def __repr__(self):
        return "<Message {}>".format(repr(self.text))
