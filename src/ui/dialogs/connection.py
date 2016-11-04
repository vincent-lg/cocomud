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

from world import World

class ConnectionDialog(wx.Dialog):

    """Connection dialog to choose a server and character."""

    def __init__(self, engine, selectionned):
        super(ConnectionDialog, self).__init__(None, title=t("common.connection"))
        self.engine = engine
        self.selectionned = selectionned

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
        worlds.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        connect.Bind(wx.EVT_BUTTON, self.OnConnect)
        edit.Bind(wx.EVT_BUTTON, self.OnEdit)
        remove.Bind(wx.EVT_BUTTON, self.OnRemove)
        add.Bind(wx.EVT_BUTTON, self.OnAdd)

    def populate_list(self, selection=0):
        """Populate the list with existing worlds."""
        self.worlds.DeleteAllItems()
        worlds = sorted(self.engine.worlds.values(), key=lambda w: w.name)
        for world in worlds:
            self.worlds.Append((world.name, world.hostname, str(world.port)))

        if worlds:
            self.worlds.Select(selection)
            self.worlds.Focus(selection)
            worlds = sorted(self.engine.worlds.values(), key=lambda w: w.name)
            try:
                world = worlds[selection]
            except IndexError:
                pass
            else:
                self.selectionned[:] = [world]

    def OnKeyDown(self, e):
        """If Enter is pressed, connect to the selected world."""
        if e.GetKeyCode() == wx.WXK_RETURN:
            self.OnConnect(e)

        e.Skip()

    def OnAdd(self, e):
        """The 'add' button is pressed."""
        world = World("")
        dialog = EditWorldDialog(self.engine, world)
        dialog.ShowModal()
        worlds = sorted(self.engine.worlds.values(), key=lambda w: w.name)
        try:
            index = worlds.index(world)
        except IndexError:
            index = 0

        self.populate_list(index)
        self.worlds.SetFocus()

    def OnEdit(self, e):
        """The 'edit' button is pressed."""
        index = self.worlds.GetFirstSelected()
        worlds = sorted(self.engine.worlds.values(), key=lambda w: w.name)
        try:
            world = worlds[index]
        except IndexError:
            wx.MessageBox(t("ui.message.world.unknown"),
                    t("ui.dialog.error"), wx.OK | wx.ICON_ERROR)
        else:
            dialog = EditWorldDialog(self.engine, world)
            dialog.ShowModal()
            self.populate_list(index)
            self.worlds.SetFocus()

    def OnRemove(self, e):
        """The 'remove' button is pressed."""
        index = self.worlds.GetFirstSelected()
        worlds = sorted(self.engine.worlds.values(), key=lambda w: w.name)
        try:
            world = worlds[index]
        except IndexError:
            wx.MessageBox(t("ui.message.world.unknown"),
                    t("ui.dialog.error"), wx.OK | wx.ICON_ERROR)
        else:
            value = wx.MessageBox(t("ui.message.world.remove"),
                    t("ui.dialog.confirm"),
                    wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            if value == wx.YES:
                del self.engine.worlds[world.name]
                world.remove()
                self.populate_list(0)
                self.worlds.SetFocus()


    def OnConnect(self, e):
        """Exit the window."""
        worlds = sorted(self.engine.worlds.values(), key=lambda w: w.name)
        index = self.worlds.GetFirstSelected()
        world = worlds[index]
        self.selectionned[:] = [world]
        self.Destroy()


class EditWorldDialog(wx.Dialog):

    """Dialog to add/edit a world."""

    def __init__(self, engine, world=None):
        if world.name:
            title = t("ui.dialog.world.edit")
        else:
            title = t("ui.dialog.world.add")

        super(EditWorldDialog, self).__init__(None, title=title)
        self.engine = engine
        self.worlds = engine.worlds
        self.world = world

        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        s_name = wx.BoxSizer(wx.HORIZONTAL)
        s_hostname = wx.BoxSizer(wx.HORIZONTAL)
        s_port = wx.BoxSizer(wx.HORIZONTAL)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.SetSizer(sizer)

        # Create the name field
        l_name = wx.StaticText(self, label=t("common.name"))
        t_name = wx.TextCtrl(self, value=self.world.name)
        self.name = t_name
        s_name.Add(l_name)
        s_name.Add(t_name)
        sizer.Add(s_name)

        # Create the hostname field
        l_hostname = wx.StaticText(self, label=t("common.hostname"))
        t_hostname = wx.TextCtrl(self, value=self.world.hostname)
        self.hostname = t_hostname
        s_hostname.Add(l_hostname)
        s_hostname.Add(t_hostname)
        sizer.Add(s_hostname)

        # Create the port field
        l_port = wx.StaticText(self, label=t("common.port"))
        t_port = wx.TextCtrl(self, value=str(self.world.port))
        self.port = t_port
        s_port.Add(l_port)
        s_port.Add(t_port)
        sizer.Add(s_port)

        # Main sizer
        sizer.Add(buttons)
        sizer.Fit(self)

        self.name.SetFocus()

        # Event binding
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

    def OnOK(self, e):
        """Save the world."""
        name = self.name.GetValue()
        hostname = self.hostname.GetValue()
        port = self.port.GetValue()
        if not name:
            wx.MessageBox(t("ui.message.world.missing"),
                    t("ui.dialog.message.missing"), wx.OK | wx.ICON_ERROR)
            self.name.SetFocus()
        elif not hostname:
            wx.MessageBox(t("ui.message.world.hostname"),
                    t("ui.dialog.message.missing"), wx.OK | wx.ICON_ERROR)
            self.hostname.SetFocus()
        elif not port:
            wx.MessageBox(t("ui.message.world.port"),
                    t("ui.dialog.message.missing"), wx.OK | wx.ICON_ERROR)
            self.port.SetFocus()
        elif not port.isdigit() or int(port) < 0 or int(port) > 65535:
            wx.MessageBox(t("ui.message.world.invalid_port"),
                    t("ui.dialog.message.invalid"), wx.OK | wx.ICON_ERROR)
            self.port.SetFocus()
        else:
            name = name.encode("utf-8", "replace")
            hostname = hostname.encode("utf-8", "replace")
            port = int(port)
            if not self.world.location:
                self.world.location = name.lower()

            self.world.name = name
            self.world.hostname = hostname
            self.world.port = port
            if self.world not in self.worlds.values():
                for name, t_world in tuple(self.worlds.items()):
                    if t_world is self.world:
                        del self.worlds[name]
            self.worlds[self.world.name] = self.world
            self.world.engine = self.engine
            self.world.save()
            self.Destroy()

    def OnCancel(self, e):
        """Simply exit the dialog."""
        self.Destroy()
