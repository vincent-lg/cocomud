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

"""This file contains the SharpEditor class."""

import wx

from ytranslate.tools import t

class SharpEditor(wx.Panel):

    """SharpScript editor panel.

    This panel can be added into dialogs that have to support SharpScript
    editing.  On the top, at the left of the panel, is a list of
    SharpScript functions which could be added to the edited SharpScript.
    On the right of this list is a set of options that will vary
    depending on the selected function.  For instance, if the user
    selects the #play SharpScript function, he/she is prompted with the
    path of the file to be played.

    At the bottom of this panel is the list of functions currently
    used in the selected attribute.

    """

    def __init__(self, dialog, engine, sharp, object, attribute):
        """Creates the frame.

        Arguments:
            dialog: the parent dialog.
            engine: the game engine.
            sharp: the SharpScript engine.
            object: the object containing the field to be edited.
            attribute: the attribute's name of the object to edit.

        If the SharpEditor is to modify a trigger, for instance,
        particularly its "action" attribute, the trigger is the object
        and "action" is the attribute's name.

        """
        wx.Panel.__init__(self, dialog)
        self.engine = engine
        self.sharp_engine = sharp
        self.object = object
        self.attribute = attribute

        # Shape
        self.functions = sorted(sharp.functions.values(),
                key=lambda function: function.name)
        self.functions = [f for f in self.functions if f.description]
        sizer = wx.BoxSizer(wx.VERTICAL)
        top = wx.BoxSizer(wx.HORIZONTAL)
        bottom = wx.BoxSizer(wx.HORIZONTAL)
        self.options = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # List of functions
        self.choices = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.choices.InsertColumn(0, "Description")
        self.populate_list()
        top.Add(self.choices)
        top.Add(self.options, proportion=3)

        # Bottom
        add = wx.Button(self, label=t("ui.button.add_action"))
        bottom.Add(add)

        # List of current functions
        self.existing = wx.ListCtrl(self,
                style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.existing.InsertColumn(0, "Function")
        self.populate_existing()

        # Buttons
        b_edit = wx.Button(self, label=t("ui.button.edit"))
        remove = wx.Button(self, label=t("ui.button.remove"))
        bottom.Add(self.existing)
        bottom.Add(b_edit)
        bottom.Add(remove)

        # Event binding
        self.choices.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.OnSelect)

    def populate_list(self):
        """Populate the list with function names."""
        self.choices.DeleteAllItems()
        for function in self.functions:
            self.choices.Append((function.description, ))

        self.choices.Select(0)
        self.choices.Focus(0)

    def populate_existing(self):
        """Populate the list with existing functions."""
        self.existing.DeleteAllItems()
        script = getattr(self.object, self.attribute)
        lines = self.sharp_engine.format(script, return_str=False)
        for line in lines:
            self.existing.Append((line, ))

        self.existing.Select(0)
        self.existing.Focus(0)

    def OnSelect(self, e):
        """When the selection changes."""
        index = self.choices.GetFirstSelected()
        try:
            function = self.functions[index]
        except IndexError:
            pass
        else:
            self.display(function)
        finally:
            e.Skip()

    def display(self, function):
        """Display the function arguments."""
        for widget in list(self.options.GetChildren()):
            widget = widget.GetWindow()
            self.options.Detach(widget)
            widget.Destroy()

        function.display(self)
