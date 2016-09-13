"""This file contains the MainWindow class."""

import wx

from dialogs.preferences import PreferencesDialog
from event import EVT_FOCUS
from scripting.key import key_name

class MainWindow(wx.Frame):

    def __init__(self, settings):
        super(MainWindow, self).__init__(None)
        self.settings = settings
        self.CreateMenuBar()
        self.InitUI()

    def CreateMenuBar(self):
        """Create the GUI menu bar and hierarchy of menus."""
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        preferences = wx.MenuItem(fileMenu, -1, '&Preferences\tAlt+Enter')
        quit = wx.MenuItem(fileMenu, -1, '&Quit\tCtrl+Q')
        fileMenu.AppendItem(preferences)
        fileMenu.AppendItem(quit)

        self.Bind(wx.EVT_MENU, self.OnPreferences, preferences)
        self.Bind(wx.EVT_MENU, self.OnQuit, quit)

        menubar.Append(fileMenu, '&File')

        self.SetMenuBar(menubar)

    def InitUI(self):
        self.panel = MUDPanel(self)
        self.SetTitle("CocoMUD client")
        self.Centre()
        self.Show()

    def OnPreferences(self, e):
        """Open the preferences dialog box."""
        dialog = PreferencesDialog(self.settings)
        dialog.ShowModal()
        dialog.Destroy()
    def OnQuit(self, e):
        self.Close()


class MUDPanel(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
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
                size=(800, 800), style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.output = t_output

        # Add the output fields in the sizer
        mainSizer.Add(l_output, pos=(1, 0))
        mainSizer.Add(t_output, pos=(10, 10))

        # Event handler
        t_input.Bind(wx.EVT_TEXT_ENTER, self.EvtText)
        t_password.Bind(wx.EVT_TEXT_ENTER, self.EvtText)
        self.Bind(EVT_FOCUS, self.OnFocus)
        t_output.Bind(wx.EVT_KEY_DOWN, self.OnKeyDownInOutput)

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

    def OnKeyDownInOutput(self, e):
        """A key is pressed while in the output."""
        modifiers = e.GetModifiers()
        key = e.GetUnicodeKey()
        if not key:
            key = e.GetKeyCode()

        name = key_name(key, modifiers)
        if name:
            print "pressing in output", name, key
        e.Skip()
