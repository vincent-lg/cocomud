# Copyright (c) 2016, LE GOFF Vincent
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

import os
import re
import sys

from accesspanel import AccessPanel
import wx
from ytranslate.tools import t

from autoupdate import AutoUpdate
from scripting.key import key_name
from ui.dialogs.alias import AliasDialog
from ui.dialogs.connection import ConnectionDialog
from ui.dialogs.loading import LoadingDialog
from ui.dialogs.macro import MacroDialog
from ui.dialogs.preferences import PreferencesDialog
from ui.dialogs.trigger import TriggerDialog
from ui.event import EVT_FOCUS, FocusEvent, myEVT_FOCUS
from updater import *
from version import BUILD

## Constants
LAST_WORD = re.compile(r"^.*?(\w+)$", re.UNICODE | re.DOTALL)

class ClientWindow(DummyUpdater):

    def __init__(self, engine, world=None):
        super(ClientWindow, self).__init__(None)
        self.panel = None
        self.engine = engine
        self.focus = True
        self.interrupt = False
        self.loading = None
        self.connection = None
        self.CreateMenuBar()
        self.InitUI(world)

    @property
    def world(self):
        return self.panel and self.panel.world or None

    def _get_client(self):
        return self.panel.client
    def _set_client(self, client):
        self.panel.client = client
    client = property(_get_client, _set_client)

    def CloseAll(self):
        """Close ALL windows (counting dialogs)."""
        windows = wx.GetTopLevelWindows()
        for window in windows:
            # The LoadingDialog needs to be destroyed to avoid confirmation
            if isinstance(window, LoadingDialog):
                window.Destroy()
            else:
                window.Close()

    def CreateMenuBar(self):
        """Create the GUI menu bar and hierarchy of menus."""
        menubar = wx.MenuBar()

        # Differemtn menus
        fileMenu = wx.Menu()
        gameMenu = wx.Menu()
        helpMenu = wx.Menu()

        ## File menu
        # Preferences
        preferences = wx.MenuItem(fileMenu, -1, t("ui.menu.preferences"))
        self.Bind(wx.EVT_MENU, self.OnPreferences, preferences)
        fileMenu.AppendItem(preferences)

        # Quit
        quit = wx.MenuItem(fileMenu, -1, t("ui.menu.quit"))
        self.Bind(wx.EVT_MENU, self.OnQuit, quit)
        fileMenu.AppendItem(quit)

        ## Game menu
        # Aliases
        alias = wx.MenuItem(gameMenu, -1, t("ui.menu.aliases"))
        self.Bind(wx.EVT_MENU, self.OnAlias, alias)
        gameMenu.AppendItem(alias)

        # Macros
        macro = wx.MenuItem(gameMenu, -1, t("ui.menu.macro"))
        self.Bind(wx.EVT_MENU, self.OnMacro, macro)
        gameMenu.AppendItem(macro)

        # Triggers
        triggers = wx.MenuItem(gameMenu, -1, t("ui.menu.triggers"))
        self.Bind(wx.EVT_MENU, self.OnTriggers, triggers)
        gameMenu.AppendItem(triggers)

        ## Help menu
        # Basics
        basics = wx.MenuItem(helpMenu, -1, t("ui.menu.help_index"))
        self.Bind(wx.EVT_MENU, self.OnBasics, basics)
        helpMenu.AppendItem(basics)

        # News
        new = wx.MenuItem(helpMenu, -1, t("ui.menu.new"))
        self.Bind(wx.EVT_MENU, self.OnNew, new)
        helpMenu.AppendItem(new)

        # Check for updates
        updates = wx.MenuItem(helpMenu, -1, t("ui.menu.updates"))
        self.Bind(wx.EVT_MENU, self.OnCheckForUpdates, updates)
        helpMenu.AppendItem(updates)

        menubar.Append(fileMenu, t("ui.menu.file"))
        menubar.Append(gameMenu, t("ui.menu.game"))
        menubar.Append(helpMenu, t("ui.menu.help"))

        self.SetMenuBar(menubar)

    def InitUI(self, world=None):
        self.create_updater(just_checking=True)
        if world is None:
            dialog = ConnectionDialog(self.engine)
            self.connection = dialog
            value = dialog.ShowModal()
            if value == wx.ID_CANCEL:
                self.Close()
                return

            world = self.engine.default_world

        self.connection = None
        self.panel = MUDPanel(self, self.engine, world)
        self.SetTitle("{} [CocoMUD]".format(world.name))
        self.Maximize()
        self.Show()
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_ACTIVATE, self.OnActivate)

    def OnPreferences(self, e):
        """Open the preferences dialog box."""
        dialog = PreferencesDialog(self.engine)
        dialog.ShowModal()
        dialog.Destroy()

    def OnAlias(self, e):
        """Open the alias dialog box."""
        dialog = AliasDialog(self.engine, self.world)
        dialog.ShowModal()
        dialog.Destroy()

    def OnMacro(self, e):
        """Open the macro dialog box."""
        dialog = MacroDialog(self.engine, self.world)
        dialog.ShowModal()
        dialog.Destroy()

    def OnTriggers(self, e):
        """Open the triggers dialog box."""
        dialog = TriggerDialog(self.engine, self.world)
        dialog.ShowModal()
        dialog.Destroy()

    def OnBasics(self, e):
        """Open the Basics help file."""
        self.engine.open_help("Basics")

    def OnNew(self, e):
        """Open the Builds help file."""
        self.engine.open_help("Builds")

    def OnCheckForUpdates(self, e):
        """Open the 'check for updates' dialog box."""
        self.create_updater(just_checking=True)
        dialog = LoadingDialog(t("ui.message.update.loading"))
        self.loading = dialog
        dialog.ShowModal()

    def OnQuit(self, e):
        self.OnClose(e)

    def OnClose(self, e):
        if self.panel.client:
            self.panel.client.running = False
        self.Destroy()

    def OnActivate(self, e):
        """The window gains focus."""
        self.focus = e.GetActive()
        e.Skip()

    def OnResponseUpdate(self, e):
        """The check for updates has returned."""
        build = e.GetValue()
        if self.loading:
            self.loading.Destroy()
            if build is None:
                message = t("ui.message.update.noupdate")
                wx.MessageBox(message, t("ui.message.information"),
                        wx.OK | wx.ICON_INFORMATION)

        if build is not None:
            message = t("ui.message.update.available", build=build)
            value = wx.MessageBox(message, t("ui.message.update.title"),
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if value == wx.YES:
                self.CloseAll()
                os.startfile("updater.exe")

    # Methods to handle client's events
    def handle_message(self, message):
        """The client has just received a message."""
        lines = message.splitlines()
        lines = [line for line in lines if line]
        message = "\n".join(lines)
        if self.panel.world:
            self.panel.world.feed_words(message)

        self.panel.Send(message)

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

class MUDPanel(AccessPanel):

    def __init__(self, parent, engine, world):
        AccessPanel.__init__(self, parent, history=True)
        self.parent = parent
        self.engine = engine
        self.client = None
        self.world = world
        self.focused = True
        self.last_ac = None

        # Event binding
        self.Bind(EVT_FOCUS, self.OnFocus)
        self.output.Bind(wx.EVT_TEXT_PASTE, self.OnPaste)

    def OnInput(self, message):
        """Some text has been sent from the input."""
        encoding = self.engine.settings["options.general.encoding"]
        message = message.encode(encoding, "replace")
        if self.world:
            self.world.reset_autocompletion()

        self.client.write(message)

    def OnFocus(self, evt):
        """The GUIClient requires a change of focus.

        This event is triggered when the GUIClient asks a change of
        focus in the input field (hiding the password field) or in
        the password field (hiding the input field).
        """
        pass
        #val = evt.GetValue()
        #if val == "input":
        #    self.input.Show()
        #    self.input.SetFocus()
        #    self.password.Hide()
        #elif val == "password":
        #    self.password.Show()
        #    self.password.SetFocus()
        #    self.input.Hide()

    def OnPaste(self, e):
        """Paste several lines in the input field.

        This event simply sends this text to be processed.

        """
        clipboard = wx.TextDataObject()
        success = wx.TheClipboard.GetData(clipboard)
        if success:
            clipboard = clipboard.GetText()
            input = clipboard
            if input.endswith("\n"):
                lines = input.splitlines()
                for line in lines:
                    self.OnInput(line)
            else:
                e.Skip()

    def OnKeyDown(self, e):
        """A key is pressed in the window."""
        modifiers = e.GetModifiers()
        key = e.GetUnicodeKey()
        if not key:
            key = e.GetKeyCode()

        if self.world:
            # Test the different macros
            for macro in self.world.macros:
                code = (macro.key, macro.modifiers)
                if code == (key, modifiers):
                    macro.execute(self.engine, self.client)
                    return

            # Test auto-completion
            if key == wx.WXK_TAB and modifiers == wx.MOD_NONE:
                input = self.input
                last_word = LAST_WORD.search(input)
                if last_word:
                    last_word = last_word.groups()[0]
                    if self.last_ac and last_word.startswith(self.last_ac):
                        # Remove the word to be modified
                        self.output.Remove(
                                self.output.GetLastPosition() + len(
                                self.last_ac) - len(last_word),
                                self.output.GetLastPosition())
                        last_word = self.last_ac
                    else:
                        self.last_ac = last_word

                    complete = self.world.find_word(last_word, TTS=True)
                    if complete:
                        end = complete[len(last_word):]
                        self.output.AppendText(end)

        AccessPanel.OnKeyDown(self, e)
