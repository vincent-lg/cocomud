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

import wx

from accesspanel.extensions.base import BaseExtension

class CommandHistory(BaseExtension):

    """Implement a command history.

    Features of command history can be set using attributes.  Here is the list of attributes, see below for an example:
        lock: what key to press to enter/leave lock mode (tuple)
        up: what key to press to go up in the history (tuple)
        down: what key to press to go down in the history (tuple)

    The attributes needing a key must be described as a tuple
    (modifiers, key) where both modifiers and keys are wxPython's key
    codes.  For instance:

    >>> import wx
    >>> from accesspanel import AccessPanel
    >>> class MyAccessPanel(AccessPanel):
    ...     def __init__(self, parent):
    ...         AccessPanel.__init__(self, parent, history=True)
    ...         # Configure the history
    ...         history = self.extensions["history"]
    ...         history.lock = (wx.MOD_NONE, wx.WXK_ESCAPE)
    ...         history.up = (wx.MOD_CONTROL, wx.WXK_UP)
    ...         history.down = (wx.MOD_CONTROL, wx.WXK_DOWN)

    Default values:
        lock: escape
        up: Ctrl + Up arrow
        down: Ctrl + Down arrow

    If you with to modify these default values, see the example above.
    If you wish to remove the features (for instance, the lock), set
    it to None.

    """

    def __init__(self, panel):
        BaseExtension.__init__(self, panel)
        self.commands = []
        self.position = -1
        self.locking = False

        # Features that can be set in the AccessPanel
        self.lock = (wx.MOD_NONE, wx.WXK_ESCAPE)
        self.up = (wx.MOD_CONTROL, wx.WXK_UP)
        self.down = (wx.MOD_CONTROL, wx.WXK_DOWN)

    def OnInput(self, text):
        """A command is sent, add it into the history."""
        self.position = -1
        for command in text.splitlines():
            if self.commands and command == self.commands[-1]:
                continue

            self.commands.append(command)

        return text

    def OnKeyDown(self, modifiers, key):
        """Add the keyboard shortcuts for the history navigation."""
        skip = False
        shortcut = (modifiers, key)
        lock_up = (wx.MOD_NONE, wx.WXK_UP)
        lock_down = (wx.MOD_NONE, wx.WXK_DOWN)

        if shortcut == self.lock:
            self.locking = not self.locking
        elif self.locking and shortcut == lock_up:
            self.GoUp()
        elif self.locking and shortcut == lock_down:
            self.GoDown()
        elif shortcut == self.up:
            self.GoUp()
        elif shortcut == self.down:
            self.GoDown()
        else:
            skip = True

        return skip

    def GoUp(self):
        """Go up in the history."""
        if self.position < 0:
            self.position = len(self.commands)
        elif self.position == 0:
            return

        self.position -= 1
        try:
            text = self.commands[self.position]
        except IndexError:
            pass
        else:
            self.panel.input = text

    def GoDown(self):
        """Go down in the history."""
        if self.position < 0:
            return
        elif self.position >= len(self.commands) - 1:
            self.position = -1
            text = ""
        else:
            self.position += 1
            try:
                text = self.commands[self.position]
            except IndexError:
                return

        self.panel.input = text
