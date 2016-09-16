"""Module containing the macro dialog."""

import wx

from scripting.key import key_code, key_name
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
        confirm = self.CreateButtonSizer(wx.OK | wx.CLOSE)
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
        b_edit = wx.Button(self, label="Edit")
        remove = wx.Button(self, label="Remove")
        edit.Add(b_edit)
        edit.Add(remove)
        add = wx.Button(self, label="Add")
        buttons.Add(add)
        buttons.Add(confirm)

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
        b_edit.Bind(wx.EVT_BUTTON, self.OnEdit)
        remove.Bind(wx.EVT_BUTTON, self.OnRemove)
        add.Bind(wx.EVT_BUTTON, self.OnAdd)
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=wx.ID_CLOSE)

    def populate_list(self, selection=0):
        """Populate the list with existing macros."""
        self.macros.DeleteAllItems()
        for macro in self.macro_list:
            self.macros.Append((macro.shortcut, macro.action))

        if self.macro_list:
            macro = self.macro_list[selection]
            self.macros.Select(selection)
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

    def OnAdd(self, e):
        """The 'add' button is pressed."""
        dialog = EditMacroDialog(self.engine, self.macro_list,
                Macro(0, 0, ""))
        dialog.ShowModal()
        self.populate_list(len(self.macro_list) - 1)
        self.macros.SetFocus()

    def OnEdit(self, e):
        """The 'edit' button is pressed."""
        index = self.macros.GetFirstSelected()
        try:
            macro = self.macro_list[index]
        except IndexError:
            wx.MessageBox("Unable to find the selected macro.",
                    wx.OK | wx.ICON_ERROR)
        else:
            dialog = EditMacroDialog(self.engine, self.macro_list, macro)
            dialog.ShowModal()
            self.populate_list(index)
            self.macros.SetFocus()

    def OnRemove(self, e):
        """The 'remove' button is pressed."""
        index = self.macros.GetFirstSelected()
        try:
            macro = self.macro_list[index]
        except IndexError:
            wx.MessageBox("Unable to find the selected macro.",
                    wx.OK | wx.ICON_ERROR)
        else:
            value = wx.MessageBox("Do you want to delete this macro? {}: " \
                    "{}".format(macro.shortcut, macro.action), "Confirm",
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if value == wx.YES:
                self.macro_list.remove(macro)
                self.populate_list(0)
                self.macros.SetFocus()

    def OnOK(self, e):
        """Save the macros."""
        macros = self.engine.macros
        macros.clear()
        for macro in self.macro_list:
            macros[(macro.key, macro.modifiers)] = macro

        self.engine.settings.write_macros()
        self.Destroy()

    def OnClose(self, e):
        """Simply exit the dialog."""
        # First, check that there hasn't been any modification
        dlg_macros = {}
        for macro in self.macro_list:
            dlg_macros[macro.key, macro.modifiers] = macro.action

        # Active macros
        act_macros = {}
        for macro in self.engine.macros.values():
            act_macros[macro.key, macro.modifiers] = macro.action

        if dlg_macros == act_macros:
            self.Destroy()
        else:
            value = wx.MessageBox("One or more macros have been modified in " \
                    "this dialog, but these modifications won't be kept " \
                    "as it is.  If you want to save these modifications, " \
                    "press 'no', then select the 'ok' button.\nDo you " \
                    "want to close this dialog and lose these modifications?",
                    "Unsaved modifications",
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if value == wx.YES:
                self.Destroy()


class EditMacroDialog(wx.Dialog):

    """Dialog to add/edit a macro."""

    def __init__(self, engine, macros, macro=None):
        if macro:
            title = "Edit a macro"
        else:
            title = "Add a macro"

        super(EditMacroDialog, self).__init__(None, title=title)
        self.engine = engine
        self.macros = macros
        self.macro = macro

        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        top = wx.BoxSizer(wx.HORIZONTAL)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.SetSizer(sizer)

        # Create the shortcut field
        s_shortcut = wx.BoxSizer(wx.VERTICAL)
        l_shortcut = wx.StaticText(self, label="Shortcut")
        t_shortcut = wx.TextCtrl(self, value=self.macro.shortcut,
                style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.shortcut = t_shortcut
        s_shortcut.Add(l_shortcut)
        s_shortcut.Add(t_shortcut)
        top.Add(s_shortcut)
        top.Add((15, -1))

        # Create the action field
        s_action = wx.BoxSizer(wx.VERTICAL)
        l_action = wx.StaticText(self, label="Action")
        t_action = wx.TextCtrl(self, value=self.macro.action,
                style=wx.TE_MULTILINE)
        self.action = t_action
        s_action.Add(l_action)
        s_action.Add(t_action)
        top.Add(s_action)

        # Main sizer
        sizer.Add(top, proportion=4)
        sizer.Add(buttons)
        sizer.Fit(self)

        self.shortcut.SetFocus()

        # Event binding
        t_shortcut.Bind(wx.EVT_KEY_DOWN, self.OnShortcutUpdate)
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

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

        e.Skip()

    def OnOK(self, e):
        """Save the macro."""
        shortcut = self.shortcut.GetValue()
        action = self.action.GetValue()
        if not shortcut:
            wx.MessageBox("The shortcut field is empty.  Please press " \
                    "the combination key you want to associate with this " \
                    "new macro.", "Missing information",
                    wx.OK | wx.ICON_ERROR)
            self.shortcut.SetFocus()
        elif not action:
            wx.MessageBox("The action field is empty.  Please specify " \
                    "the actions associated with this macro.",
                    "Missing information", wx.OK | wx.ICON_ERROR)
            self.action.SetFocus()
        else:
            shortcut = shortcut.encode("utf-8", "replace")
            action = action.encode("utf-8", "replace")
            key, modifiers = key_code(shortcut)
            self.macro.key = key
            self.macro.modifiers = modifiers
            self.macro.action = action
            if self.macro not in self.macros:
                self.macros.append(self.macro)
            self.Destroy()

    def OnCancel(self, e):
        """Simply exit the dialog."""
        self.Destroy()
