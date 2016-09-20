"""This file contains the MainWindow class."""

import wx

from ytranslate.tools import t

from dialogs.preferences import PreferencesDialog
from dialogs.macro import MacroDialog
from ui.event import EVT_FOCUS, FocusEvent, myEVT_FOCUS

class MainWindow(wx.Frame):

    def __init__(self, engine):
        super(MainWindow, self).__init__(None)
        self.engine = engine
        self.CreateMenuBar()
        self.InitUI()

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

    def InitUI(self):
        self.panel = MUDPanel(self, self.engine)
        self.SetTitle("CocoMUD client")
        self.Maximize()
        self.Show()

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
        self.Close()

    # Methods to handle client's events
    def handle_message(self, message):
        """The client has just received a message."""
        pos = self.panel.output.GetInsertionPoint()
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

    def __init__(self, parent, engine):
        wx.Panel.__init__(self, parent)
        self.engine = engine
        self.client = None

        mainSizer = wx.GridBagSizer(5, 5)

        # Input
        l_input = wx.StaticText(self, -1, "Input")
        t_input = wx.TextCtrl(self, -1, "", size=(125, -1),
                style=wx.TE_PROCESS_ENTER)
        self.input = t_input

        # Password
        l_password = wx.StaticText(self, -1, "Password")
        t_password = wx.TextCtrl(self, -1, "", size=(20, -1),
                style=wx.TE_PROCESS_ENTER | wx.TE_PASSWORD)
        self.password = t_password
        t_password.Hide()

        # Add the input field in the sizer
        mainSizer.Add(l_input, pos=(0, 0))
        mainSizer.Add(t_input, pos=(0, 1), span=(1, 6))
        mainSizer.Add(l_password, pos=(0, 7))
        mainSizer.Add(t_password, pos=(0, 8), span=(1, 2))

        # Ouput
        l_output = wx.StaticText(self, -1, "Output")
        t_output = wx.TextCtrl(self, -1, "",
                size=(600, 600), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.output = t_output

        # Add the output fields in the sizer
        mainSizer.Add(l_output, pos=(1, 0))
        mainSizer.Add(t_output, pos=(10, 10))

        # Event handler
        t_input.Bind(wx.EVT_TEXT_ENTER, self.EvtText)
        t_password.Bind(wx.EVT_TEXT_ENTER, self.EvtText)
        self.Bind(EVT_FOCUS, self.OnFocus)
        t_input.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        t_password.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        t_output.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def EvtText(self, event):
        """One of the input fields is sending text."""
        self.input.Clear()
        self.password.Clear()
        msg = event.GetString().encode("utf-8", "replace")
        self.client.write(msg + "\r\n")

    def OnFocus(self, evt):
        val = evt.GetValue()
        if val == "input":
            self.input.Show()
            self.input.SetFocus()
            self.password.Hide()
        elif val == "password":
            self.password.Show()
            self.password.SetFocus()
            self.input.Hide()

    def OnKeyDown(self, e):
        """A key is pressed in the window."""
        modifiers = e.GetModifiers()
        key = e.GetUnicodeKey()
        if not key:
            key = e.GetKeyCode()

        # Look for matching macros
        for code, macro in self.engine.macros.items():
            if code == (key, modifiers):
                macro.execute(self.engine, self.client)

        e.Skip()
