# Copyright (c) 2023, LE GOFF Vincent
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

"""Module containing the Writevar function class."""

import wx

from sharp import Function

class Writevar(Function):

    """Function SharpScript 'writevar'."""

    description = "Write a variable in memory"

    def run(self, variable, contents):
        """Write a variable."""
        if self.world:
            engine = self.world.sharp_engine
            if contents:
                contents = engine.replace_variables(contents)
                engine.locals[variable] = contents
            else:
                engine.locals.pop(variable, None)

    def display(self, dialog, variable="", contents=""):
        """Display the function's argument."""
        l_variable = self.t("variable", "Name of the variable to write in")
        l_contents = self.t(
            "contents",
            (
                "The variable contents (it can contain other variables "
                "with the $variable syntax)"
            )
        )

        # Variable
        l_variable = wx.StaticText(dialog, label=l_variable)
        t_variable = wx.TextCtrl(dialog, value=variable)
        dialog.variable = t_variable
        dialog.top.Add(l_variable)
        dialog.top.Add(t_variable)

        # Contents
        l_contents = wx.StaticText(dialog, label=l_contents)
        t_contents = wx.TextCtrl(dialog, value=contents)
        dialog.contents = t_contents
        dialog.top.Add(l_contents)
        dialog.top.Add(t_contents)

    def complete(self, dialog):
        """The user pressed 'ok' in the dialog."""
        variable = dialog.variable.GetValue()
        empty_variable = self.t("empty_variable",
                "The variable name is empty.  Where to write in memory?")

        if not variable:
            wx.MessageBox(empty_variable, t("ui.message.error"),
                    wx.OK | wx.ICON_ERROR)
            dialog.variable.SetFocus()
            return None

        contents = dialog.contents.GetValue()

        arguments = [variable, contents]
        return tuple(arguments)
