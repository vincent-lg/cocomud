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

"""Module containing the Worlds dialog."""

from __future__ import absolute_import
from zipfile import ZipFile

import wx
from ytranslate import t

from task.download import Download
from wizard.install_world import InstallWorld

class WorldsDialog(wx.Dialog):

    """Worlds dialog to search, download and install a world."""

    def __init__(self, engine, worlds):
        wx.Dialog.__init__(self, None, title=t("ui.dialog.worlds.title"))
        self.engine = engine
        self.online = worlds
        self.online.sort()
        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Create the dialog
        worlds = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        worlds.InsertColumn(0, t("common.name"))
        worlds.InsertColumn(1, t("ui.dialog.worlds.author"))
        worlds.InsertColumn(2, t("ui.dialog.worlds.last_updated"))
        self.worlds = worlds

        # Description field
        l_description = wx.StaticText(self, label=t("common.description"))
        self.description = wx.TextCtrl(self, size=(600, 400),
                style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Buttons
        install = wx.Button(self, label=t("ui.dialog.worlds.install"))

        # Main sizer
        sizer.Add(worlds, proportion=4)
        sizer.Add(l_description)
        sizer.Add(self.description, proportion=2)
        sizer.Add(install)
        sizer.Fit(self)

        # Populate the list
        self.populate_list()
        self.worlds.SetFocus()

        # Event binding
        self.worlds.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.OnSelect)
        install.Bind(wx.EVT_BUTTON, self.OnInstall)

    def populate_list(self, selection=0):
        """Populate the list with worlds."""
        self.worlds.DeleteAllItems()

        for name, author, updated_on, description, a in self.online:
            updated_on = "{}-{:>02}-{:>02}".format(updated_on.year,
                    updated_on.month, updated_on.day)
            self.worlds.Append((name, author, updated_on))

        if self.online:
            try:
                world = self.online[selection]
            except IndexError:
                pass
            else:
                self.description.SetValue(world.description)
                self.worlds.Select(selection)
                self.worlds.Focus(selection)

    def OnSelect(self, e):
        """When the selection changes."""
        index = self.worlds.GetFirstSelected()
        try:
            world = self.online[index]
        except IndexError:
            wx.MessageBox(t("ui.dialog.worlds.unknown_world"),
                    t("ui.alert.error"), wx.OK | wx.ICON_ERROR)
        else:
            self.description.SetValue(world.description)

    def OnInstall(self, e):
        """The user clicked on 'install'>"""
        index = self.worlds.GetFirstSelected()
        try:
            world = self.online[index]
        except IndexError:
            wx.MessageBox(t("ui.dialog.worlds.unknown_world"),
                    t("ui.alert.error"), wx.OK | wx.ICON_ERROR)
        else:
            attachment = world.attachments[0]
            url = attachment.content_url
            download = Download(None, url)
            download.start()

            # Extract the world in memory
            archive = ZipFile(download.file)
            files = {name: archive.read(name) for name in archive.namelist()}
            wizard = InstallWorld(self.engine, world.name, files)
            self.Destroy()
            wizard.start()
