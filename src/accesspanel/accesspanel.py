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

"""Module containing the AccessPanel class.

The AccessPanel is a child of wx.Panel.  It behaves like an ordinary
panel with a multi-line text field taking all available room.  This
output field can serve as input:

If the user types in the output field, the cursor is moved to the
bottom of the text field where he/she can type.  The AccessPanel is
like a big read-only text area, except for the last line(s).

Additional features:
1.  Command history
    The AccessPanel supports a command history, meaning it will
    remember what command has been entered and will allow to navigate
    through the command history using CTRL + arrow keys.
    You can activate it by setting the 'history' argument to True
    when creating an AccessPanel.
2.  Lock input
    The AccessPanel can lock the user in the input, meaning the user
    cannot leave the input field using tab or shift-tab.
3.  ANSI support
    ANSI codes are displayed in the AccessPanel.  See the 'ANSI'
    extension for more details.

"""

from collections import OrderedDict

import wx

from . import extensions

## Constants
# Navigation keys (arrows, home/end, pageUp/pageDown...)
NAV_KEYS = set()
NAV_KEYS.add(wx.WXK_UP)
NAV_KEYS.add(wx.WXK_DOWN)
NAV_KEYS.add(wx.WXK_LEFT)
NAV_KEYS.add(wx.WXK_RIGHT)
NAV_KEYS.add(wx.WXK_HOME)
NAV_KEYS.add(wx.WXK_END)
NAV_KEYS.add(wx.WXK_PAGEUP)
NAV_KEYS.add(wx.WXK_PAGEDOWN)
NAV_KEYS.add(wx.WXK_NUMLOCK)
NAV_KEYS.add(wx.WXK_PAUSE)
NAV_KEYS.add(wx.WXK_CAPITAL)
NAV_KEYS.add(wx.WXK_SCROLL)
NAV_KEYS.add(wx.WXK_WINDOWS_LEFT)
NAV_KEYS.add(wx.WXK_WINDOWS_RIGHT)
NAV_KEYS.add(wx.WXK_CONTROL)
NAV_KEYS.add(wx.WXK_SHIFT)

# Event definition
myEVT_MESSAGE = wx.NewEventType()
EVT_MESSAGE = wx.PyEventBinder(myEVT_MESSAGE, 1)

class MessageEvent(wx.PyCommandEvent):

    """Event when a message is received."""

    def __init__(self, etype, eid, value=None, pos=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value
        self._pos = pos

    def GetValue(self):
        """Return the event's value."""
        return self._value

    def GetPos(self):
        """Return the event's value."""
        return self._pos


## AccessPanel class
class AccessPanel(wx.Panel):

    """Access panel with a text field (TextCtrl) in it.

    Constructor:
        parent: the parent window where the panel is defined.
        history (default False): activate command history.
        lock_input (default False): activate the lock in input.
        ansi (default False): activate the ANSI extension.

    Example:
    >>> import wx
    >>> from accesspanel import AccessPanel
    >>> class MyAccessPanel(AccessPanel):
    ...     def __init__(self, parent):
    ...         AccessPanel.__init__(self, parent, history=True)
    ...
    ...     def OnInput(self, text):
    ...         print "I received", input
    >>>
    >>> class MainWindow(wx.Frame):
    ...     def __init__(self):
    ...         wx.Frame.__init__(self, None)
    ...         self.panel = MyAccessPanel(self)
    ...         # Write something in the text field
    ...         self.panel.send("This is a text\nThat you shouldn't edit.")
    ...         self.Maximize()
    ...         self.show()

    Attributes and properties:
        output: The output text field (the TextCtrl)
        input: the text contained in the lines allowed for editing

    Methods:
        IsEditing: is the cursor in the editing section?
        OnInput: text is sent by the user pressing RETURN.
        ClearInput: the input text is cleared.
        Send: send text to the output field (it will added in the output).

    """

    def __init__(self, parent, rich=True, history=False, lock_input=False,
            ansi=False):
        super(AccessPanel, self).__init__(parent)
        self.editing_pos = 0
        self.extensions = OrderedDict()
        self.rich = rich
        self.screenreader_support = True

        # Build the extensions
        if history:
            extension = extensions.CommandHistory(self)
            self.extensions["history"] = extension
        if lock_input:
            extension = extensions.LockInput(self)
            self.extensions["lock_input"] = extension
        if ansi:
            extension = extensions.ANSI(self)
            self.extensions["ANSI"] = extension

        # Window design
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Output field
        if rich:
            style = wx.TE_MULTILINE | wx.TE_RICH
        else:
            style = wx.TE_MULTILINE

        output = wx.TextCtrl(self, size=(600, 400), style=style)
        self.output = output

        # Add the output field in the sizer
        sizer.Add(output, 1, wx.EXPAND)

        # Event handler
        self.Bind(EVT_MESSAGE, self.OnMessage)
        output.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        # Panel design
        sizer.Fit(self)

    def _get_input(self):
        """Return the text being edited.

        This text should be between the editing position (editing_pos)
        and the end of the output field.

        """
        return self.output.GetRange(
                self.editing_pos, self.output.GetLastPosition())

    def _set_input(self, text):
        """Set the text in the input field."""
        self.ClearInput()
        self.output.AppendText(text)
        self.output.SetInsertionPoint(self.output.GetInsertionPoint())
    input = property(_get_input, _set_input)

    def IsEditing(self, beyond_one=False):
        """Return True if editing, False otherwise.

        We consider the user is editing if the cursor is in the input area.

        The 'beyond_one' parameter can be set to True if we want to
        test whether the cursor is at least one character ahead in
        the input field.

        """
        pos = self.output.GetInsertionPoint()
        if beyond_one:
            pos -= 1

        return pos < self.editing_pos

    def ClearInput(self):
        """Clear the input text."""
        self.output.Remove(
                self.editing_pos, self.output.GetLastPosition())
        self.editing_pos = self.output.GetLastPosition()

    def ClearOutput(self):
        """Clear the output."""
        self.editing_pos = 0
        self.output.Clear()

        # Trigger extensions
        for extension in self.extensions.values():
            extension.OnClearOutput()

    def OnInput(self, message):
        """A message has been sent by pressing RETURN.

        This method should be overridden in child classes.

        """
        pass

    def OnMessage(self, e):
        """A message is received and should be displayed in the output field.

        This method is directly called in answer to the EVT_MESSAGE.
        It displays the received text in the window, being careful to
        put the cursor where it was before, with the typed text in
        the input field.

        """
        origin = pos = self.output.GetInsertionPoint()
        if not self.screenreader_support:
            self.output.Freeze()

        message = e.GetValue()
        mark = e.GetPos()

        # Normalize new lines
        message = "\r\n".join(message.splitlines())

        # Modify the text based on extensions
        for extension in self.extensions.values():
            message = extension.OnMessage(message)
            if not message:
                return

        if not message.endswith("\r\n"):
            message += "\r\n"

        # Get the text before the editing line
        output = self.output.GetRange(0, self.editing_pos)
        input = self.input

        # Clears the output field and pastes the text back in
        self.ClearInput()
        self.output.AppendText(message)

        # If the cursor is beyond the editing position
        if pos >= self.editing_pos:
            if self.rich:
                pos += len(message.replace("\r\n", "\n"))
            else:
                pos += len(message)

        # We have added some text, the editing position should be
        # at the end of the text
        self.editing_pos = self.output.GetLastPosition()
        self.output.AppendText(input)

        # Call the extensions' PostMessage
        for extension in self.extensions.values():
            extension.PostMessage(message)

        if not self.screenreader_support:
            self.output.Thaw()

        # If there's a mark
        if mark:
            self.output.SetInsertionPoint(origin + mark)
        else:
            self.output.SetInsertionPoint(pos)

    def Send(self, message, pos=None):
        """Create an event to send the message to the window."""
        evt = MessageEvent(myEVT_MESSAGE, -1, message, pos)
        wx.PostEvent(self, evt)

    def OnKeyDown(self, e):
        """A key is pressed in the output field."""
        skip = True
        pos = self.output.GetInsertionPoint()
        input = self.input
        modifiers = e.GetModifiers()
        key = e.GetUnicodeKey()
        if not key:
            key = e.GetKeyCode()

        # If the user has pressed RETURN
        if key == wx.WXK_RETURN and modifiers == 0:
            self.ClearInput()

            # Call the extensions' 'OnInput'
            for extension in self.extensions.values():
                input = extension.OnInput(input)
                if not input:
                    break

            self.OnInput(input)
            skip = False

        # If we press a letter before the input area, move it back there
        if pos < self.editing_pos and modifiers in (wx.MOD_NONE, wx.MOD_SHIFT):
            if key not in NAV_KEYS:
                self.output.SetInsertionPoint(self.output.GetLastPosition())
                pos = self.output.GetInsertionPoint()

        # If we press backspace out of the input area
        if key == wx.WXK_BACK and modifiers == 0 and self.IsEditing(True):
            skip = False

        # Call the extensions' 'OnKeyDown' method
        if skip:
            for extension in self.extensions.values():
                skip = extension.OnKeyDown(modifiers, key)
                if not skip:
                    return

        if skip:
            e.Skip()
