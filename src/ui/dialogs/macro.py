"""Module containing the macro dialog."""

import wx

from scripting.key import key_name
from scripting.macro import Macro

class MacroDialog(wx.Dialog):

    """Macro dialog."""

    def __init__(self, engine):
        super(MacroDialog, self).__init__(None, title="Macros")
        self.engine = engine

        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        top = wx.BoxSizer(wx.HORIZONTAL)
        edit = wx.BoxSizer(wx.VERTICAL)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)

        # Create the dialog
        macros = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        macros.InsertColumn(0, "Shortcut")
        macros.InsertColumn(1, "Action")
        self.macros = macros

        # Create the edit field
        s_shortcut = wx.BoxSizer(wx.HORIZONTAL)
        l_shortcut = wx.StaticText(self, label="Shortcut")
        t_shortcut = wx.TextCtrl(self, value="",
                style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.shortcut = t_shortcut
        s_shortcut.Add(l_shortcut)
        s_shortcut.Add(t_shortcut)
        edit.Add(s_shortcut)
        edit.Add((-1, 20))

        # Buttons
        add = wx.Button(self, label="Add")
        remove = wx.Button(self, label="Remove")
        save = wx.Button(self, label="Save")
        close = wx.Button(self, label="Cancel")
        buttons.Add(add)
        buttons.Add(remove)
        buttons.Add(save)
        buttons.Add(close)

        # Main sizer
        top.Add(macros, proportion=2)
        top.Add((20, -1))
        top.Add(edit)
        sizer.Add(top, proportion=4)
        sizer.Add(buttons)
        sizer.Fit(self)

        # Populate the list
        self.macro_list = []
        macro_list = sorted(list(self.engine.macros.values()),
                key=lambda macro: macro.shortcut)
        for macro in macro_list:
            # Copy the macro, so it can be modified by the dialog
            # without modifying the settings
            macro = macro.copied
            self.macro_list.append(macro)

        self.populate_list()
        self.macros.SetFocus()

        # Event binding
        macros.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.OnSelect)
        t_shortcut.Bind(wx.EVT_KEY_DOWN, self.OnShortcutUpdate)

    def populate_list(self, selection=0):
        """Populate the list with existing macros."""
        self.macros.DeleteAllItems()
        for macro in self.macro_list:
            self.macros.Append((macro.shortcut, macro.action))

        if self.macro_list:
            macro = self.macro_list[selection]
            self.macros.Focus(selection)
            self.shortcut.SetValue(macro.shortcut)

    def OnShortcutUpdate(self, e):
        """A key is pressed in the shortcut area."""
        modifiers = e.GetModifiers()
        key = e.GetUnicodeKey()
        if not key:
            key = e.GetKeyCode()

        # Is that a valid shortcut
        name = key_name(key, modifiers)
        if name:
            self.shortcut.SetValue(name)
            self.shortcut.SelectAll()

            # Update the information in the table
            index = self.macros.GetFirstSelected()
            if index < 0:
                index = 0

            try:
                macro = self.macro_list[index]
            except IndexError:
                pass
            else:
                macro.key = key
                macro.modifiers = modifiers
                self.populate_list(index)

        e.Skip()

    def OnSelect(self, e):
        """When the selection changes."""
        index = self.macros.GetFirstSelected()
        try:
            macro = self.macro_list[index]
        except IndexError:
            pass
        else:
            self.shortcut.SetValue(macro.shortcut)
            self.shortcut.SelectAll()
