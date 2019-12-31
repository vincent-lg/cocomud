# Copyright (c) 2016-2020, LE GOFF Vincent
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

from __future__ import absolute_import
from zipfile import ZipFile

import wx
from ytranslate import t

from task.import_worlds import ImportWorlds
from ui.dialogs.worlds import WorldsDialog
from world import World
from wizard.install_world import InstallWorld

class ConnectionDialog(wx.Dialog):

    """Connection dialog to choose a server and character."""

    def __init__(self, engine, session):
        super(ConnectionDialog, self).__init__(None, title=t("common.connection"))
        self.engine = engine
        self.session = session

        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        top = wx.BoxSizer(wx.HORIZONTAL)
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)

        # Create the dialog
        worlds = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        worlds.InsertColumn(0, t("common.name"))
        worlds.InsertColumn(1, t("common.hostname"))
        worlds.InsertColumn(2, t("common.port"))
        self.worlds = worlds

        # Characters
        characters = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        characters.InsertColumn(0, t("common.name"))
        self.characters = characters

        # Buttons
        connect = wx.Button(self, label=t("ui.button.connect"))
        add = wx.Button(self, label=t("ui.button.add"))
        edit = wx.Button(self, label=t("ui.button.edit"))
        remove = wx.Button(self, label=t("ui.button.remove"))
        b_import = wx.Button(self, label=t("ui.menu.import"))
        buttons.Add(connect)
        buttons.Add(add)
        buttons.Add(edit)
        buttons.Add(remove)
        buttons.Add(b_import)

        # Main sizer
        top.Add(worlds)
        top.Add(characters)
        sizer.Add(top)
        sizer.Add(buttons)
        sizer.Fit(self)

        # Populate the list
        self.populate_list()
        self.worlds.SetFocus()

        # Event binding
        worlds.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        worlds.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.OnSelectWorld)
        characters.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        connect.Bind(wx.EVT_BUTTON, self.OnConnect)
        edit.Bind(wx.EVT_BUTTON, self.OnEdit)
        remove.Bind(wx.EVT_BUTTON, self.OnRemove)
        add.Bind(wx.EVT_BUTTON, self.OnAdd)
        b_import.Bind(wx.EVT_BUTTON, self.OnImport)

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
                self.session.world = world

                # Change the world's characters
                self.characters.DeleteAllItems()
                self.characters.Append((t("ui.client.any_character"), ))
                self.characters.Select(0)
                self.characters.Focus(0)
                characters = sorted(world.characters.values(),
                        key=lambda c: c.location)
                for i, character in enumerate(characters):
                    self.characters.Append((character.name, ))
                    if character.default:
                        self.characters.Select(i + 1)
                        self.characters.Focus(i + 1)

    def OnSelectWorld(self, e):
        """When the selection changes."""
        index = self.worlds.GetFirstSelected()
        worlds = sorted(self.engine.worlds.values(), key=lambda w: w.name)
        try:
            world = worlds[index]
        except IndexError:
            pass
        else:
            characters = sorted(world.characters.values(),
                    key=lambda c: c.location)
            self.characters.DeleteAllItems()
            self.characters.Append((t("ui.client.any_character"), ))
            self.characters.Select(0)
            self.characters.Focus(0)
            for i, character in enumerate(characters):
                self.characters.Append((character.name, ))
                if character.default:
                    self.characters.Select(i + 1)
                    self.characters.Focus(i + 1)

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
        except ValueError:
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
                    t("ui.alert.error"), wx.OK | wx.ICON_ERROR)
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
                    t("ui.alert.error"), wx.OK | wx.ICON_ERROR)
        else:
            value = wx.MessageBox(t("ui.message.world.remove"),
                    t("ui.alert.confirm"),
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

        # Look for the character
        characters = sorted(world.characters.values(),
                key=lambda c: c.location)
        index = self.characters.GetFirstSelected()
        if index > 0:
            character = characters[index - 1]
        else:
            character = None

        self.session.world = world
        self.session.character = character
        self.EndModal(wx.ID_OK)

    def OnImport(self, e):
        """The user clicked on the import button."""
        self.PopupMenu(ImportPopupMenu(self))


class EditWorldDialog(wx.Dialog):

    """Dialog to add/edit a world."""

    def __init__(self, engine, world=None):
        if world.name:
            title = t("ui.message.world.edit")
        else:
            title = t("ui.message.world.add")

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
        s_protocol = wx.BoxSizer(wx.HORIZONTAL)
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

        # Create the protocol radio button
        l_protocol = wx.StaticText(self, label=t("common.protocol"))
        telnet = wx.RadioButton(self, label=t("common.telnet"),
                style=wx.RB_GROUP)
        SSL = wx.RadioButton(self, label=t("common.SSL"))
        is_telnet = self.world.protocol.lower() == "telnet"
        telnet.SetValue(is_telnet)
        SSL.SetValue(not is_telnet)
        self.telnet = telnet
        self.SSL = SSL
        s_protocol.Add(l_protocol)
        s_protocol.Add(telnet)
        s_protocol.Add(SSL)
        sizer.Add(s_protocol)

        # Main sizer
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
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
        telnet = self.telnet.GetValue()
        protocol = "telnet" if telnet else "SSL"
        if not name:
            wx.MessageBox(t("ui.message.world.missing"),
                    t("ui.alert.missing"), wx.OK | wx.ICON_ERROR)
            self.name.SetFocus()
        elif not hostname:
            wx.MessageBox(t("ui.message.world.hostname"),
                    t("ui.alert.missing"), wx.OK | wx.ICON_ERROR)
            self.hostname.SetFocus()
        elif not port:
            wx.MessageBox(t("ui.message.world.port"),
                    t("ui.alert.missing"), wx.OK | wx.ICON_ERROR)
            self.port.SetFocus()
        elif not port.isdigit() or int(port) < 0 or int(port) > 65535:
            wx.MessageBox(t("ui.message.world.invalid_port"),
                    t("ui.alert.invalid"), wx.OK | wx.ICON_ERROR)
            self.port.SetFocus()
        else:
            port = int(port)
            if not self.world.location:
                self.world.location = name.lower()

            self.world.name = name
            self.world.hostname = hostname
            self.world.port = port
            self.world.protocol = protocol
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


class ImportPopupMenu(wx.Menu):

    """Popup menu that appears when clicking on the import button."""

    def __init__(self, parent):
        wx.Menu.__init__(self)
        self.parent = parent

        # Create the sub-menu
        on_disk = wx.MenuItem(self, wx.NewId(), t("ui.menu.import_on_disk"))
        self.AppendItem(on_disk)
        self.Bind(wx.EVT_MENU, self.OnDisk, on_disk)
        online = wx.MenuItem(self, wx.NewId(), t("ui.menu.import_online"))
        self.AppendItem(online)
        self.Bind(wx.EVT_MENU, self.Online, online)

    def OnDisk(self, e):
        """Import a world on disk."""
        choose_file = t("ui.button.choose_file")
        extensions = "Zip archive (*.zip)|*.zip"
        dialog = wx.FileDialog(None, choose_file,
                "", "", extensions, wx.FD_OPEN)
        result = dialog.ShowModal()
        if result == wx.ID_OK:
            filename = dialog.GetPath()

            # Try to install the world from the archive
            archive = ZipFile(filename)
            files = {name: archive.read(name) for name in archive.namelist()}
            options = files.get("world/options.conf")
            if options:
                infos = World.get_infos(options)
                name = infos.get("connection", {}).get("name")
                wizard = InstallWorld(self.parent.engine, name, files)
                wizard.start()
                self.parent.populate_list()
                self.parent.worlds.SetFocus()

    def Online(self, e):
        """Import a world online."""
        task = ImportWorlds()
        task.start()
        dialog = WorldsDialog(self.parent.engine, task.worlds)
        dialog.ShowModal()
        self.parent.populate_list()
        self.parent.worlds.SetFocus()
