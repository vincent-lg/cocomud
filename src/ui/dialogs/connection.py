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

"""Module containing the connection dialog."""

import wx

from ytranslate import t

class ConnectionDialog(wx.Dialog):

    """Connection dialog to choose a server and character."""

    def __init__(self, engine):
        super(ConnectionDialog, self).__init__(None, title=t("common.connection"))
        self.engine = engine
        self.selected = None

        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)

        # Create the dialog
        worlds = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        worlds.InsertColumn(0, t("common.name"))
        worlds.InsertColumn(1, t("common.hostname"))
        worlds.InsertColumn(2, t("common.port"))
        self.worlds = worlds

        # Buttons
        connect = wx.Button(self, label=t("ui.button.connect"))
        add = wx.Button(self, label=t("ui.button.add"))
        edit = wx.Button(self, label=t("ui.button.edit"))
        remove = wx.Button(self, label=t("ui.button.remove"))
        buttons.Add(connect)
        buttons.Add(add)
        buttons.Add(edit)
        buttons.Add(remove)

        # Main sizer
        sizer.Add(worlds, proportion=4)
        sizer.Add(buttons)
        sizer.Fit(self)

        # Populate the list
        self.populate_list()
        self.worlds.SetFocus()

        # Event binding
        connect.Bind(wx.EVT_BUTTON, self.OnConnect)
        #b_edit.Bind(wx.EVT_BUTTON, self.OnEdit)
        #remove.Bind(wx.EVT_BUTTON, self.OnRemove)
        #add.Bind(wx.EVT_BUTTON, self.OnAdd)

    def populate_list(self, selection=0):
        """Populate the list with existing worlds."""
        self.worlds.DeleteAllItems()
        worlds = sorted(self.engine.worlds.values(), key=lambda w: w.name)
        for world in worlds:
            self.worlds.Append((world.name, world.hostname, str(world.port)))

        if worlds:
            self.worlds.Select(selection)
            self.worlds.Focus(selection)

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
            wx.MessageBox(t("ui.dialog.message.unknown_macro"),
                    wx.OK | wx.ICON_ERROR)
        else:
            value = wx.MessageBox(t("ui.dialog.message.remove_macro",
            shortcut=macro.shortcut, action=macro.action),
            t("ui.dialog.confirm"),
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
            value = wx.MessageBox(t("ui.dialog.message.unsaved_macros"),
                    t("ui.dialog.confirm"),
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if value == wx.YES:
                self.Destroy()

    def OnConnect(self, e):
        """Exit the window."""
        worlds = sorted(self.engine.worlds.values(), key=lambda w: w.name)
        index = self.worlds.GetFirstSelected()
        world = worlds[index]
        self.engine.default_world = world
        self.Destroy()
