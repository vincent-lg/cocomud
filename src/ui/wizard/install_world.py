# Copyright (c) 2016, LE GOFF Vincent
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

"""Module containing the dialog to import a world."""

from collections import OrderedDict
import json
import wx
from ytranslate import t

class PreInstallDialog(wx.Dialog):

    """Dialog to pre-install a world."""

    def __init__(self, engine, name, worlds, merging):
        wx.Dialog.__init__(self, None,
                title="Preparing to install the world {}".format(name))
        self.engine = engine
        self.name = name
        self.worlds = worlds
        self.merging = merging
        self.results = {}
        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)

        # Create the dialog
        choices = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        choices.InsertColumn(0, "World")
        self.choices = choices

        # Create the list of choices
        for i, choice in enumerate(self.worlds):
            if not choice.name:
                text = "New world"
            else:
                text = choice.name

            if i == 0:
                text += " (recommended)"

            choices.Append((text, ))

        choices.Select(0)
        choices.Focus(0)

        # Name field
        s_name = wx.BoxSizer(wx.VERTICAL)
        l_name = wx.StaticText(self, label="Name")
        self.name = wx.TextCtrl(self, value=self.name)
        s_name.Add(l_name)
        s_name.Add(self.name)

        # Disable the name if world already has one
        if self.worlds[0].name:
            self.name.Disable()

        # Merging methods
        methods = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        methods.InsertColumn(0, "Column")
        self.methods = methods

        # Create the list of merging methods
        for method in self.merging:
            methods.Append((method, ))

        methods.Select(0)
        methods.Focus(0)

        # Buttons
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)

        # Main sizer
        sizer.Add(choices)
        sizer.Add(s_name)
        sizer.Add(methods)
        sizer.Add(buttons)
        sizer.Fit(self)

        # Event binding
        choices.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.OnSelect)
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

    def OnSelect(self, e):
        """When the selection changes."""
        index = self.choices.GetFirstSelected()
        try:
            world = self.worlds[index]
        except IndexError:
            pass
        else:
            if world.name:
                self.name.Disable()
            else:
                self.name.Enable()
                self.name.SelectAll()

    def OnOK(self, e):
        """The user pressed on OK."""
        name = self.name.GetValue()
        index = self.choices.GetFirstSelected()
        merging = ["ignore", "replace"]
        try:
            world = self.worlds[index]
        except IndexError:
            wx.MessageBox("Cannot find the world.",
                    t("ui.alert.error"), wx.OK | wx.ICON_ERROR)
        else:
            index = self.methods.GetFirstSelected()
            try:
                method = merging[index]
            except IndexError:
                wx.MessageBox("Cannot find the merging method.",
                        t("ui.alert.error"), wx.OK | wx.ICON_ERROR)
            else:
                # Check that the location isn't already being used
                for other in self.engine.worlds.values():
                    if other is world:
                        continue

                    if other.location == name.lower():
                        wx.MessageBox(
                                "A world already exists at that location.", t("ui.alert.error"),
                                wx.OK | wx.ICON_ERROR)
                        return

                # Check that the name is valid
                if not name and not world.name:
                    wx.MessageBox(
                            "The name of this world is invalid.",
                            t("ui.alert.error"), wx.OK | wx.ICON_ERROR)
                    return

                self.results["world"] = world
                self.results["merge"] = method
                self.results["name"] = name
                self.Destroy()

    def OnCancel(self, e):
        """Simply destroy the dialog."""
        self.Destroy()


class InstallWorld(wx.Dialog):

    """Wizard-dialog to isntall a world."""

    def __init__(self, engine, wizard):
        wx.Dialog.__init__(self, None, title="Installing the world {}".format(
                wizard.name))
        self.engine = engine
        self.wizard = wizard
        self.data = {}
        self.widgets = OrderedDict()
        self.choices = {}
        self.InitUI()
        self.Center()

    def InitUI(self):
        """Create the install dialog according to the install file."""
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Create the dialog
        install = self.wizard.files.get("world/install.json")
        if install:
            values = json.loads(install, encoding="utf-8",
                    object_pairs_hook=OrderedDict)

        # Create each widget
        i = 0
        line = wx.BoxSizer(wx.HORIZONTAL)
        for key, value in values.items():
            if i > 2:
                sizer.Add(line)
                line = wx.BoxSizer(wx.HORIZONTAL)
                i = 0

            type = value.get("type", "invalid")
            text = value.get("name", "No name")
            default = value.get("default")
            if type == "str":
                default = default or ""
                mini = wx.BoxSizer(wx.VERTICAL)
                label = wx.StaticText(self, label=text)
                widget = wx.TextCtrl(self, value=default)
                widget.SelectAll()
                mini.Add(label)
                mini.Add(widget)
                line.Add(mini)
            elif type == "bool":
                widget = wx.CheckBox(self, label=text)
                widget.SetValue(bool(default))
                line.Add(widget)
            elif type == "choice":
                mini = wx.BoxSizer(wx.VERTICAL)
                label = wx.StaticText(self, label=text)
                widget = wx.ListCtrl(self,
                        style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
                mini.Add(label)
                mini.Add(widget)
                line.Add(mini)

                # Create the colums
                nb = 0
                for column in value.get("columns", []):
                    widget.InsertColumn(nb, column)
                    nb += 1

                # Append the various choices to the list
                choices = []
                for choice in value.get("list", []):
                    sub_key = choice.get("key", "unknown")
                    name = choice.get("name", "no name")
                    if isinstance(name, list):
                        name = [str(e) for e in name]
                        widget.Append(tuple(name))
                    else:
                        widget.Append((name, ))
                    choices.append(sub_key)
                self.choices[key] = choices
                widget.Select(0)
                widget.Focus(0)

            self.widgets[key] = widget
            i += 1
        sizer.Add(line)

        # Buttons
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(buttons)

        # Select the first widget
        first = list(self.widgets.values())[0]
        first.SetFocus()

        # Event binding
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

    def OnOK(self, e):
        """Install the world."""
        for key, widget in self.widgets.items():
            if isinstance(widget, wx.ListCtrl):
                index = widget.GetFirstSelected()
                try:
                    value = self.choices[key][index]
                except (KeyError, IndexError):
                    continue
            else:
                value = widget.GetValue()

            self.data[key] = value

        self.Destroy()

    def OnCancel(self, e):
        """Simply exit the dialog."""
        self.Destroy()
