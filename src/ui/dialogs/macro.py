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

"""Module containing the macro dialog."""

import wx

from ytranslate import t

from scripting.key import key_code, key_name
from scripting.macro import Macro
from ui.sharp_editor import SharpEditor

class MacroDialog(wx.Dialog):

    """Macro dialog."""

    def __init__(self, engine, world):
        super(MacroDialog, self).__init__(None, title=t("common.macro", 2))
        self.engine = engine
        self.world = world

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
        macros.InsertColumn(0, t("common.shortcut"))
        macros.InsertColumn(1, t("common.action"))
        self.macros = macros

        # Create the edit field
        s_shortcut = wx.BoxSizer(wx.HORIZONTAL)
        l_shortcut = wx.StaticText(self, label=t("common.shortcut"))
        t_shortcut = wx.TextCtrl(self, value="",
                style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.shortcut = t_shortcut
        s_shortcut.Add(l_shortcut)
        s_shortcut.Add(t_shortcut)
        edit.Add(s_shortcut)
        edit.Add((-1, 20))

        # Buttons
        b_edit = wx.Button(self, label=t("ui.button.edit"))
        remove = wx.Button(self, label=t("ui.button.remove"))
        edit.Add(b_edit)
        edit.Add(remove)
        add = wx.Button(self, label=t("ui.button.add"))
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
        macro_list = sorted(list(self.world.macros),
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
                Macro(0, 0, ""), self.world)
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
            dialog = EditMacroDialog(self.engine, self.macro_list,
                    macro, self.world)
            dialog.ShowModal()
            self.populate_list(index)
            self.macros.SetFocus()

    def OnRemove(self, e):
        """The 'remove' button is pressed."""
        index = self.macros.GetFirstSelected()
        try:
            macro = self.macro_list[index]
        except IndexError:
            wx.MessageBox(t("ui.message.macro.unknown"),
                    t("ui.alert.error"), wx.OK | wx.ICON_ERROR)
        else:
            value = wx.MessageBox(t("ui.message.macro.remove",
            shortcut=macro.shortcut, action=macro.action),
            t("ui.alert.confirm"),
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if value == wx.YES:
                self.macro_list.remove(macro)
                self.populate_list(0)
                self.macros.SetFocus()

    def OnOK(self, e):
        """Save the macros."""
        macros = self.world.macros
        macros[:] = []
        for macro in self.macro_list:
            macro.sharp_engine = self.world.sharp_engine
            macros.append(macro)

        self.world.save_config()
        self.Destroy()

    def OnClose(self, e):
        """Simply exit the dialog."""
        # First, check that there hasn't been any modification
        dlg_macros = {}
        for macro in self.macro_list:
            dlg_macros[macro.key, macro.modifiers] = macro.action

        # Active macros
        act_macros = {}
        for macro in self.world.macros:
            act_macros[macro.key, macro.modifiers] = macro.action

        if dlg_macros == act_macros:
            self.Destroy()
        else:
            value = wx.MessageBox(t("ui.message.macro.unsaved"),
                    t("ui.alert.confirm"),
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if value == wx.YES:
                self.Destroy()


class EditMacroDialog(wx.Dialog):

    """Dialog to add/edit a macro."""

    def __init__(self, engine, macros, macro, world):
        if macro.shortcut:
            title = t("ui.message.macro.edit")
        else:
            title = t("ui.message.macro.add")

        super(EditMacroDialog, self).__init__(None, title=title)
        self.engine = engine
        self.macros = macros
        self.macro = macro
        self.world = world

        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        top = wx.BoxSizer(wx.HORIZONTAL)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.SetSizer(sizer)

        # Create the shortcut field
        s_shortcut = wx.BoxSizer(wx.VERTICAL)
        l_shortcut = wx.StaticText(self, label=t("common.shortcut"))
        t_shortcut = wx.TextCtrl(self, value=self.macro.shortcut,
                style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.shortcut = t_shortcut
        s_shortcut.Add(l_shortcut)
        s_shortcut.Add(t_shortcut)
        top.Add(s_shortcut)

        # SharpScript editor
        self.editor = SharpEditor(self, self.engine, self.world.sharp_engine,
                self.macro, "action", text=True, escape=True)

        # Main sizer
        sizer.Add(top, proportion=4)
        sizer.Add(self.editor)
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
        action = self.editor.text.GetValue()
        if not shortcut:
            wx.MessageBox(t("ui.message.macro.missing_macro"),
                    t("ui.alert.missing"), wx.OK | wx.ICON_ERROR)
            self.shortcut.SetFocus()
        elif not action:
            wx.MessageBox(t("ui.message.macro.missing_action"),
                    t("ui.alert.missing"), wx.OK | wx.ICON_ERROR)
            self.editor.SetFocus()
        else:
            #shortcut = shortcut.encode("utf-8", "replace")
            #action = action.encode("utf-8", "replace")
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
