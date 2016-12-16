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
