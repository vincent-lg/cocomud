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

"""Module containing the alias dialog."""

import wx

from ytranslate import t

from scripting.alias import Alias
from ui.sharp_editor import SharpEditor

class AliasDialog(wx.Dialog):

    """Alias dialog."""

    def __init__(self, engine, world):
        super(AliasDialog, self).__init__(None, title=t("common.alias", 2))
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
        aliases = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        aliases.InsertColumn(0, t("common.name"))
        aliases.InsertColumn(1, t("common.action"))
        self.aliases = aliases

        # Buttons
        b_edit = wx.Button(self, label=t("ui.button.edit"))
        remove = wx.Button(self, label=t("ui.button.remove"))
        edit.Add(b_edit)
        edit.Add(remove)
        add = wx.Button(self, label=t("ui.button.add"))
        buttons.Add(add)
        buttons.Add(confirm)
        help = wx.Button(self, label=t("ui.button.help"))
        buttons.Add(help)

        # Main sizer
        top.Add(aliases, proportion=2)
        top.Add((20, -1))
        top.Add(edit)
        sizer.Add(top, proportion=4)
        sizer.Add(buttons)
        sizer.Fit(self)

        # Populate the list
        self.alias_list = [alias.copied for alias in self.world.aliases]
        self.alias_list = sorted(self.alias_list,
                key=lambda alias: alias.alias)
        self.populate_list()
        self.aliases.SetFocus()

        # Event binding
        b_edit.Bind(wx.EVT_BUTTON, self.OnEdit)
        remove.Bind(wx.EVT_BUTTON, self.OnRemove)
        add.Bind(wx.EVT_BUTTON, self.OnAdd)
        help.Bind(wx.EVT_BUTTON, self.OnHelp)
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=wx.ID_CLOSE)

    def populate_list(self, selection=0):
        """Populate the list with existing aliases."""
        self.aliases.DeleteAllItems()
        for alias in self.alias_list:
            self.aliases.Append((alias.alias, alias.action))

        if self.alias_list:
            alias = self.alias_list[selection]
            self.aliases.Select(selection)
            self.aliases.Focus(selection)

    def OnAdd(self, e):
        """The 'add' button is pressed."""
        sharp = self.world.sharp_engine
        dialog = EditAliasDialog(self.engine, self.world, self.alias_list,
                Alias(sharp, "", ""))
        dialog.ShowModal()
        self.populate_list(len(self.alias_list) - 1)
        self.aliases.SetFocus()

    def OnEdit(self, e):
        """The 'edit' button is pressed."""
        index = self.aliases.GetFirstSelected()
        try:
            alias = self.alias_list[index]
        except IndexError:
            wx.MessageBox("Unable to find the selected alias.",
                    wx.OK | wx.ICON_ERROR)
        else:
            dialog = EditAliasDialog(self.engine, self.world,
                    self.alias_list, alias)
            dialog.ShowModal()
            self.populate_list(index)
            self.aliases.SetFocus()

    def OnRemove(self, e):
        """The 'remove' button is pressed."""
        index = self.aliases.GetFirstSelected()
        try:
            alias = self.alias_list[index]
        except IndexError:
            wx.MessageBox(t("ui.message.alias.unknown"),
                    t("ui.dialog.error"), wx.OK | wx.ICON_ERROR)
        else:
            value = wx.MessageBox(t("ui.message.alias.remove",
                    alias=alias.alias), t("ui.dialog.confirm"),
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if value == wx.YES:
                self.alias_list.remove(alias)
                self.populate_list(0)
                self.aliases.SetFocus()

    def OnHelp(self, e):
        """The user clicked on 'help'."""
        self.engine.open_help("Alias")

    def OnOK(self, e):
        """Save the aliases."""
        aliases = self.world.aliases
        aliases[:] = []
        for alias in self.alias_list:
            alias.sharp_engine = self.world.sharp_engine
            aliases.append(alias)

        self.world.save_config()
        self.Destroy()

    def OnClose(self, e):
        """Simply exit the dialog."""
        # First, check that there hasn't been any modification
        dlg_aliases = {}
        for alias in self.alias_list:
            dlg_aliases[alias.alias] = alias.action

        # Active aliases
        act_aliases = {}
        for alias in self.world.aliases:
            act_aliases[alias.alias] = alias.action

        if dlg_aliases == act_aliases:
            self.Destroy()
        else:
            value = wx.MessageBox(t("ui.message.alias.unsaved"),
                    t("ui.dialog.confirm"),
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if value == wx.YES:
                self.Destroy()


class EditAliasDialog(wx.Dialog):

    """Dialog to add/edit an alias."""

    def __init__(self, engine, world, aliases, alias=None):
        if alias.alias:
            title = t("ui.dialog.alias.edit")
        else:
            title = t("ui.dialog.alias.add")

        super(EditAliasDialog, self).__init__(None, title=title)
        self.engine = engine
        self.world = world
        self.aliases = aliases
        self.alias = alias

        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        top = wx.BoxSizer(wx.HORIZONTAL)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.SetSizer(sizer)

        # Create the alias field
        s_alias = wx.BoxSizer(wx.VERTICAL)
        l_alias = wx.StaticText(self, label=t("common.alias", 1))
        t_alias = wx.TextCtrl(self, value=self.alias.alias)
        self.t_alias = t_alias
        s_alias.Add(l_alias)
        s_alias.Add(t_alias)
        top.Add(s_alias)
        top.Add((15, -1))

        # Main sizer
        sizer.Add(top, proportion=4)

        # SharpScript editor
        self.editor = SharpEditor(self, self.engine, self.world.sharp_engine,
                self.alias, "action")
        sizer.Add(self.editor)
        sizer.Add(buttons)
        sizer.Fit(self)

        self.t_alias.SetFocus()

        # Event binding
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

    def OnOK(self, e):
        """Save the alias."""
        alias = self.t_alias.GetValue()
        action = self.alias.action
        if not alias:
            wx.MessageBox(t("ui.message.alias.missing_alias"),
                    t("ui.dialog.message.missing"), wx.OK | wx.ICON_ERROR)
            self.t_alias.SetFocus()
        elif not action:
            wx.MessageBox(t("ui.message.alias.missing_action"),
                    t("ui.dialog.message.missing"), wx.OK | wx.ICON_ERROR)
        else:
            alias = alias
            self.alias.alias = alias
            self.alias.action = action
            self.alias.re_alias = self.alias.find_regex(self.alias.alias)
            if self.alias not in self.aliases:
                self.aliases.append(self.alias)
            self.Destroy()

    def OnCancel(self, e):
        """Simply exit the dialog."""
        self.Destroy()
