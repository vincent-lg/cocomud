# Copyright (c) 2016-2026, LE GOFF Vincent
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

"""Module containing the event dialog."""

import wx

from ytranslate import t

from scripting.event import Event
from ui.sharp_editor import SharpEditor

class EventDialog(wx.Dialog):

    """Event dialog: the world's #event handlers."""

    def __init__(self, engine, world):
        super(EventDialog, self).__init__(None, title=t("common.event", 2))
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
        events = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        events.InsertColumn(0, t("common.event", 1))
        events.InsertColumn(1, t("common.action"))
        self.events = events

        # Buttons
        b_edit = wx.Button(self, label=t("ui.button.edit"))
        remove = wx.Button(self, label=t("ui.button.remove"))
        edit.Add(b_edit)
        edit.Add(remove)
        add = wx.Button(self, label=t("ui.button.add"))
        buttons.Add(add)
        buttons.Add(confirm)

        # Main sizer
        top.Add(events, proportion=2)
        top.Add((20, -1))
        top.Add(edit)
        sizer.Add(top, proportion=4)
        sizer.Add(buttons)
        sizer.Fit(self)

        # Populate the list
        self.event_list = sorted([event.copied for event in
                self.world.events], key=lambda event: event.key.lower())
        self.populate_list()
        self.events.SetFocus()

        # Event binding
        b_edit.Bind(wx.EVT_BUTTON, self.OnEdit)
        remove.Bind(wx.EVT_BUTTON, self.OnRemove)
        add.Bind(wx.EVT_BUTTON, self.OnAdd)
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnClose, id=wx.ID_CLOSE)

    def populate_list(self, selection=0):
        """Populate the list with existing event handlers."""
        self.events.DeleteAllItems()
        for event in self.event_list:
            self.events.Append((event.key, event.action))

        if self.event_list:
            selection = max(0, min(selection, len(self.event_list) - 1))
            self.events.Select(selection)
            self.events.Focus(selection)

    def selected(self):
        """Return the selected event handler, or None."""
        index = self.events.GetFirstSelected()
        if 0 <= index < len(self.event_list):
            return self.event_list[index]

        wx.MessageBox(t("ui.message.event.unknown"),
                t("ui.alert.error"), wx.OK | wx.ICON_ERROR)
        return None

    def OnAdd(self, e):
        """The 'add' button is pressed."""
        sharp = self.world.sharp_engine
        dialog = EditEventDialog(self.engine, self.world, self.event_list,
                Event(sharp, "", ""))
        dialog.ShowModal()
        dialog.Destroy()
        self.populate_list(len(self.event_list) - 1)
        self.events.SetFocus()

    def OnEdit(self, e):
        """The 'edit' button is pressed."""
        event = self.selected()
        if event is not None:
            index = self.event_list.index(event)
            dialog = EditEventDialog(self.engine, self.world,
                    self.event_list, event)
            dialog.ShowModal()
            dialog.Destroy()
            self.populate_list(index)
            self.events.SetFocus()

    def OnRemove(self, e):
        """The 'remove' button is pressed."""
        event = self.selected()
        if event is not None:
            index = self.event_list.index(event)
            value = wx.MessageBox(t("ui.message.event.remove",
                    event=event.key), t("ui.alert.confirm"),
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if value == wx.YES:
                self.event_list.remove(event)
                self.populate_list(index)
                self.events.SetFocus()

    def OnOK(self, e):
        """Save the event handlers."""
        with self.world.lock:
            events = self.world.events
            events[:] = []
            for event in self.event_list:
                event.sharp_engine = self.world.sharp_engine
                events.append(event)

        self.world.save_config()
        self.EndModal(wx.ID_OK)

    def OnClose(self, e):
        """Exit the dialog, confirming if there are changes."""
        dialog = sorted((event.key, event.action)
                for event in self.event_list)
        active = sorted((event.key, event.action)
                for event in self.world.events)

        if dialog == active:
            self.EndModal(wx.ID_CANCEL)
        else:
            value = wx.MessageBox(t("ui.message.event.unsaved"),
                    t("ui.alert.confirm"),
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if value == wx.YES:
                self.EndModal(wx.ID_CANCEL)


class EditEventDialog(wx.Dialog):

    """Dialog to add or edit an event handler: a key and actions."""

    def __init__(self, engine, world, events, event):
        if event.key:
            title = t("ui.message.event.edit")
        else:
            title = t("ui.message.event.add")

        super(EditEventDialog, self).__init__(None, title=title)
        self.engine = engine
        self.world = world
        self.events = events
        self.event = event

        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.SetSizer(sizer)

        # The event key
        l_key = wx.StaticText(self, label=t("ui.message.event.key"))
        t_key = wx.TextCtrl(self, value=self.event.key)
        self.t_key = t_key
        sizer.Add(l_key)
        sizer.Add(t_key)

        # SharpScript editor
        self.editor = SharpEditor(self, self.engine, self.world.sharp_engine,
                self.event, "action")
        sizer.Add(self.editor)
        sizer.Add(buttons)
        sizer.Fit(self)

        self.t_key.SetFocus()

        # Event binding
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

    def OnOK(self, e):
        """Save the event handler."""
        key = self.t_key.GetValue().strip()
        if not key:
            wx.MessageBox(t("ui.message.event.missing_key"),
                    t("ui.alert.missing"), wx.OK | wx.ICON_ERROR)
            self.t_key.SetFocus()
            return

        for other in self.events:
            if other is not self.event and other.matches(key):
                wx.MessageBox(t("ui.message.event.duplicate", event=key),
                        t("ui.alert.error"), wx.OK | wx.ICON_ERROR)
                self.t_key.SetFocus()
                return

        self.event.key = key
        if self.event not in self.events:
            self.events.append(self.event)
        self.EndModal(wx.ID_OK)

    def OnCancel(self, e):
        """Simply exit the dialog."""
        self.EndModal(wx.ID_CANCEL)
