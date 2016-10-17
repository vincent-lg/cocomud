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

"""Module containing the trigger dialog."""

import wx

from ytranslate import t

from scripting.trigger import Trigger
from ui.sharp_editor import SharpEditor

class TriggerDialog(wx.Dialog):

    """Trigger dialog."""

    def __init__(self, engine, world):
        super(TriggerDialog, self).__init__(None, title=t("common.trigger", 2))
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
        triggers = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        triggers.InsertColumn(0, t("common.name"))
        triggers.InsertColumn(1, t("common.action"))
        self.triggers = triggers

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
        top.Add(triggers, proportion=2)
        top.Add((20, -1))
        top.Add(edit)
        sizer.Add(top, proportion=4)
        sizer.Add(buttons)
        sizer.Fit(self)

        # Populate the list
        self.trigger_list = [trigger.copied for trigger in \
                self.world.triggers]
        self.trigger_list = sorted(self.trigger_list,
                key=lambda trigger: trigger.reaction)
        self.populate_list()
        self.triggers.SetFocus()

        # Event binding
        b_edit.Bind(wx.EVT_BUTTON, self.OnEdit)
        remove.Bind(wx.EVT_BUTTON, self.OnRemove)
        add.Bind(wx.EVT_BUTTON, self.OnAdd)
        help.Bind(wx.EVT_BUTTON, self.OnHelp)
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=wx.ID_CLOSE)

    def populate_list(self, selection=0):
        """Populate the list with existing triggers."""
        self.triggers.DeleteAllItems()
        for trigger in self.trigger_list:
            self.triggers.Append((trigger.reaction, trigger.action))

        if self.trigger_list:
            trigger = self.trigger_list[selection]
            self.triggers.Select(selection)
            self.triggers.Focus(selection)

    def OnAdd(self, e):
        """The 'add' button is pressed."""
        sharp = self.world.sharp_engine
        dialog = EditTriggerDialog(self.engine, self.world, self.trigger_list,
                Trigger(sharp, "", ""))
        dialog.ShowModal()
        self.populate_list(len(self.trigger_list) - 1)
        self.triggers.SetFocus()

    def OnEdit(self, e):
        """The 'edit' button is pressed."""
        index = self.triggers.GetFirstSelected()
        try:
            trigger = self.trigger_list[index]
        except IndexError:
            wx.MessageBox(t("ui.message.trigger.unknown"),
                    t("ui.dialog.error"), wx.OK | wx.ICON_ERROR)
        else:
            dialog = EditTriggerDialog(self.engine, self.world,
                    self.trigger_list, trigger)
            dialog.ShowModal()
            self.populate_list(index)
            self.triggers.SetFocus()

    def OnRemove(self, e):
        """The 'remove' button is pressed."""
        index = self.triggers.GetFirstSelected()
        try:
            trigger = self.trigger_list[index]
        except IndexError:
            wx.MessageBox(t("ui.message.trigger.unknown"),
                    t("ui.dialog.error"), wx.OK | wx.ICON_ERROR)
        else:
            value = wx.MessageBox(t("ui.message.trigger.remove",
                    trigger=trigger.reaction), t("ui.dialog.confirm"),
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if value == wx.YES:
                self.trigger_list.remove(trigger)
                self.populate_list(0)
                self.triggers.SetFocus()

    def OnHelp(self, e):
        """The user clicked on 'help'."""
        self.engine.open_help("Trigger")

    def OnOK(self, e):
        """Save the triggers."""
        triggers = self.world.triggers
        triggers[:] = []
        for trigger in self.trigger_list:
            trigger.sharp_engine = self.world.sharp_engine
            triggers.append(trigger)

        self.world.save_config()
        self.Destroy()

    def OnClose(self, e):
        """Simply exit the dialog."""
        # First, check that there hasn't been any modification
        dlg_triggers = {}
        for trigger in self.trigger_list:
            dlg_triggers[trigger.reaction] = trigger.action

        # Active triggers
        act_triggers = {}
        for trigger in self.world.triggers:
            act_triggers[trigger.reaction] = trigger.action

        if dlg_triggers == act_triggers:
            self.Destroy()
        else:
            value = wx.MessageBox(t("ui.message.trigger.unsaved"),
                    t("ui.dialog.confirm"),
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if value == wx.YES:
                self.Destroy()


class EditTriggerDialog(wx.Dialog):

    """Dialog to add/edit a trigger."""

    def __init__(self, engine, world, triggers, trigger=None):
        if trigger.reaction:
            title = t("ui.message.trigger.edit")
        else:
            title = t("ui.message.trigger.add")

        super(EditTriggerDialog, self).__init__(None, title=title)
        self.engine = engine
        self.world = world
        self.triggers = triggers
        self.trigger = trigger

        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        top = wx.BoxSizer(wx.HORIZONTAL)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.SetSizer(sizer)

        # Create the trigger field
        s_trigger = wx.BoxSizer(wx.VERTICAL)
        l_trigger = wx.StaticText(self, label=t("common.trigger", 1))
        t_trigger = wx.TextCtrl(self, value=self.trigger.reaction)
        self.t_trigger = t_trigger
        s_trigger.Add(l_trigger)
        s_trigger.Add(t_trigger)
        top.Add(s_trigger)
        top.Add((15, -1))

        # Main sizer
        sizer.Add(top, proportion=4)

        # SharpScript editor
        self.editor = SharpEditor(self, self.engine, self.world.sharp_engine,
                self.trigger, "action")
        sizer.Add(self.editor)
        sizer.Add(buttons)
        sizer.Fit(self)

        self.t_trigger.SetFocus()

        # Event binding
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

    def OnOK(self, e):
        """Save the trigger."""
        reaction = self.t_trigger.GetValue()
        action = self.trigger.action
        if not reaction:
            wx.MessageBox(t("ui.message.trigger.missing_reaction"),
                    t("ui.dialog.message.missing"), wx.OK | wx.ICON_ERROR)
            self.t_trigger.SetFocus()
        elif not action:
            wx.MessageBox(t("ui.message.trigger.missing_action"),
                    t("ui.dialog.message.missing"), wx.OK | wx.ICON_ERROR)
        else:
            trigger = trigger
            self.trigger.reaction = trigger
            self.trigger.action = action
            self.trigger.re_reaction = self.trigger.find_regex(
                    self.trigger.reaction)
            if self.trigger not in self.triggers:
                self.triggers.append(self.trigger)
            self.Destroy()

    def OnCancel(self, e):
        """Simply exit the dialog."""
        self.Destroy()
