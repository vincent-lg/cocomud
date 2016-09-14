"""Module containing the macro dialog."""

import wx

from scripting.key import key_name

class MacroDialog(wx.Dialog):

    """Macro dialog."""

    def __init__(self, engine):
        super(MacroDialog, self).__init__(None, title="Macroes")
        self.engine = engine

        self.InitUI()
        self.Maximize()

    def InitUI(self):
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(15, 15)
        panel.SetSizer(sizer)

        # Create the dialog
        macro_label = wx.StaticText(panel, label="Macros")
        macro_list = wx.ComboBox(panel, choices=[], style=wx.CB_READONLY)
        self.macro = macro_list
        shortcut_label = wx.StaticText(panel, label="Shortcut")
        shortcut = wx.TextCtrl(self, value="", name="Press a key combination",
                style=wx.TE_READONLY)
        self.shortcut = shortcut

        # Append to the sizer
        sizer.Add(macro_label, pos=(0, 0))
        sizer.Add(macro_list, pos=(1, 0), span=(5, 1))
        sizer.Add(shortcut_label, pos=(0, 2))
        sizer.Add(shortcut, pos=(1, 2))

        # Event binding
        macro_list.Bind(wx.EVT_COMBOBOX, self.OnSelect)
        shortcut.Bind(wx.EVT_KEY_DOWN, self.OnKeyDownInShortcut)

    def OnSelect(self, e):
        """When the selection changes."""
        selection = e.GetString()
        self.shortcut.SetValue(selection)

    def OnOK(self, e):
        """Save the preferences."""
        settings = self.engine.settings
        tts = self.tabs.TTS
        settings["options.TTS.on"] = tts.TTS_on.GetValue()
        settings["options.TTS.outside"] = tts.TTS_outside.GetValue()
        settings["options"].write()
        self.Destroy()

    def OnCancel(self, e):
        """Simply exit the dialog."""
        self.Destroy()

    def OnKeyDownInShortcut(self, e):
        """A key is pressed while in the shortcut field."""
        modifiers = e.GetModifiers()
        key = e.GetUnicodeKey()
        if not key:
            key = e.GetKeyCode()

        name = key_name(key, modifiers)
        if name:
            self.shortcut.Clear()
            self.shortcut.SetValue(name)
            self.shortcut.SelectAll()

        e.Skip()
