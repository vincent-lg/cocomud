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

"""This file contains the ClientWindow class."""

import wx

from ytranslate.tools import t

from scripting.key import key_name
from ui.dialogs.connection import ConnectionDialog
from ui.dialogs.macro import MacroDialog
from ui.dialogs.preferences import PreferencesDialog
from ui.event import EVT_FOCUS, FocusEvent, myEVT_FOCUS

class ClientWindow(wx.Frame):

    def __init__(self, engine, world=None):
        super(ClientWindow, self).__init__(None)
        self.engine = engine
        self.CreateMenuBar()
        self.InitUI(world)

    def _get_client(self):
        return self.panel.client
    def _set_client(self, client):
        self.panel.client = client
    client = property(_get_client, _set_client)

    def CreateMenuBar(self):
        """Create the GUI menu bar and hierarchy of menus."""
        menubar = wx.MenuBar()

        # Differemtn menus
        fileMenu = wx.Menu()
        gameMenu = wx.Menu()

        # File menu
        ## Preferences
        preferences = wx.MenuItem(fileMenu, -1, t("ui.menu.preferences"))
        self.Bind(wx.EVT_MENU, self.OnPreferences, preferences)
        fileMenu.AppendItem(preferences)

        ## Quit
        quit = wx.MenuItem(fileMenu, -1, t("ui.menu.quit"))
        self.Bind(wx.EVT_MENU, self.OnQuit, quit)
        fileMenu.AppendItem(quit)

        # Game menu
        macro = wx.MenuItem(fileMenu, -1, t("ui.menu.macro"))
        self.Bind(wx.EVT_MENU, self.OnMacro, macro)
        gameMenu.AppendItem(macro)

        menubar.Append(fileMenu, t("ui.menu.file"))
        menubar.Append(gameMenu, t("ui.menu.game"))

        self.SetMenuBar(menubar)

    def InitUI(self, world=None):
        if world is None:
            dialog = ConnectionDialog(self.engine)
            dialog.ShowModal()
            world = self.engine.default_world

        self.panel = MUDPanel(self, self.engine, world)
        self.SetTitle("CocoMUD client")
        self.Maximize()
        self.Show()
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnPreferences(self, e):
        """Open the preferences dialog box."""
        dialog = PreferencesDialog(self.engine)
        dialog.ShowModal()
        dialog.Destroy()

    def OnMacro(self, e):
        """Open the macro dialog box."""
        dialog = MacroDialog(self.engine)
        dialog.ShowModal()
        dialog.Destroy()

    def OnQuit(self, e):
        self.OnClose(e)

    def OnClose(self, e):
        if self.panel.client:
            self.panel.client.running = False
        self.Destroy()

    # Methods to handle client's events
    def handle_message(self, message):
        """The client has just received a message."""
        pos = self.panel.output.GetInsertionPoint()
        lines = message.splitlines()
        lines = [line for line in lines if line]
        message = "\n".join(lines)
        output = self.panel.output.GetValue()
        if output and not output.endswith("\n"):
            message = "\n" + message

        if self.engine.settings["options.accessibility.nl_end"]:
            message += "\n"

        self.panel.output.write(message)
        self.panel.output.SetInsertionPoint(pos)

    def handle_option(self, command):
        """Handle the specified option.

        The command is a string representing the received option.
        The following options are supported:
            "hide":  the input should be hidden
            "show":  the input should be shown

        """
        if command == "hide":
            evt = FocusEvent(myEVT_FOCUS, -1, "password")
            wx.PostEvent(self.panel, evt)
        elif command == "show":
            evt = FocusEvent(myEVT_FOCUS, -1, "input")
            wx.PostEvent(self.panel, evt)

class MUDPanel(wx.Panel):

    def __init__(self, parent, engine, world):
        wx.Panel.__init__(self, parent)
        self.engine = engine
        self.client = None
        self.world = world
        self.index = -1
        self.history = []
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Input
        s_input = wx.BoxSizer(wx.HORIZONTAL)
        l_input = wx.StaticText(self, -1, t("ui.client.input"))
        t_input = wx.TextCtrl(self, -1, "", size=(125, -1),
                style=wx.TE_PROCESS_ENTER)
        self.input = t_input

        # Password
        l_password = wx.StaticText(self, -1, t("ui.client.password"))
        t_password = wx.TextCtrl(self, -1, "", size=(20, -1),
                style=wx.TE_PROCESS_ENTER | wx.TE_PASSWORD)
        self.password = t_password
        t_password.Hide()

        # Add the input field in the sizer
        s_input.Add(l_input)
        s_input.Add(t_input, proportion=4)
        s_input.Add(l_password)
        s_input.Add(t_password, proportion=2)

        # Ouput
        l_output = wx.StaticText(self, -1, t("ui.client.output"))
        t_output = wx.TextCtrl(self, -1, "",
                size=(600, 400), style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_PROCESS_TAB)
        self.output = t_output

        # Add the output fields in the sizer
        sizer.Add(s_input)
        sizer.Add(t_output, proportion=8)

        # Event handler
        t_input.Bind(wx.EVT_TEXT_ENTER, self.EvtText)
        t_password.Bind(wx.EVT_TEXT_ENTER, self.EvtText)
        self.Bind(EVT_FOCUS, self.OnFocus)
        t_input.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        t_input.Bind(wx.EVT_SET_FOCUS, self.OnInputFocused)
        t_password.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        t_output.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def EvtText(self, event):
        """One of the input fields is sending text."""
        self.input.Clear()
        self.password.Clear()
        encoding = self.engine.settings["options.general.encoding"]
        msg = event.GetString().encode(encoding, "replace")
        self.client.write(msg + "\r\n")

        # Write in the history
        if event.GetEventObject() == self.input:
            if self.index == -1 and msg:
                self.history.append(msg)

    def OnFocus(self, evt):
        """The GUIClient requires a change of focus.

        This event is triggered when the GUIClient asks a change of
        focus in the input field (hiding the password field) or in
        the password field (hiding the input field).
        """
        val = evt.GetValue()
        if val == "input":
            self.input.Show()
            self.input.SetFocus()
            self.password.Hide()
        elif val == "password":
            self.password.Show()
            self.password.SetFocus()
            self.input.Hide()

    def OnInputFocused(self, e):
        """Input gains the focus."""
        message = self.input.GetValue()
        if message:
            self.input.SetInsertionPoint(len(message) + 1)
        e.Skip()

    def OnKeyDown(self, e):
        """A key is pressed in the window."""
        skip = True
        modifiers = e.GetModifiers()
        key = e.GetUnicodeKey()
        if not key:
            key = e.GetKeyCode()

        if e.GetEventObject() == self.input:
            skip = self.HandleHistory(modifiers, key)

        # Look for matching macros
        for code, macro in self.engine.macros.items():
            if code == (key, modifiers):
                macro.execute(self.engine, self.client)

        if e.GetEventObject() is self.output:
            shortcut = key_name(key, modifiers)
            if shortcut:
                if shortcut == "Backspace" or len(shortcut) == 1 or (
                        shortcut.startswith("Shift +") and len(shortcut) == 9):
                    self.input.EmulateKeyPress(e)
        elif e.GetEventObject() == self.input:
            if key == wx.WXK_TAB:
                if self.engine.settings["options.accessibility.tab_end"]:
                    message = self.output.GetValue()
                    self.output.SetInsertionPoint(-1)

        if skip:
            e.Skip()

    def HandleHistory(self, modifiers, key):
        """Handle the history commands."""
        if modifiers == 0:
            if key == wx.WXK_UP:
                self.HistoryGoUp()
                return False
            elif key == wx.WXK_DOWN:
                self.HistoryGoDown()
                return False

        return True

    def HistoryGoUp(self):
        """Go up in the history."""
        if self.index == -1:
            self.index = len(self.history) - 1
        elif self.index > 0:
            self.index -= 1
        else:
            return

        message = self.history[self.index]
        encoding = self.engine.settings["options.general.encoding"]
        message = message.decode(encoding, "replace")
        self.input.Clear()
        self.input.SetValue(message)
        self.input.SetInsertionPoint(-1)

    def HistoryGoDown(self):
        """Go down in the history."""
        if self.index == -1:
            return
        elif self.index >= len(self.history) - 1:
            self.index = -1
            message = ""
        else:
            self.index += 1
            message = self.history[self.index]

        encoding = self.engine.settings["options.general.encoding"]
        message = message.decode(encoding, "replace")
        self.input.Clear()
        self.input.SetValue(message)
        self.input.SetInsertionPoint(-1)
