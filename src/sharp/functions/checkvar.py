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

"""Module containing the Checkvar function class."""

import wx

from sharp import Function
from sharp.exceptions import ScriptInterrupt

class Checkvar(Function):

    """Function SharpScript 'checkvar'."""

    description = "Check if a variable exists in memory"

    def run(self, variable, error):
        """Say an error if the variable doesn't exist."""
        exists = False
        if self.sharp_engine:
            engine = self.sharp_engine
            exists = variable in engine.locals

        if self.client:
            if not exists:
                if error:
                    self.client.handle_message(error)
                raise ScriptInterrupt

    def display(self, dialog, variable="", error=""):
        """Display the function's argument."""
        l_variable = self.t("variable", "Name of the variable to check")
        l_error = self.t(
            "error",
            (
                "The error message to display if the variable doesn't "
                "exist.  If empty, no message will be displayed, "
                "but the script will simply terminate."
            )
        )

        # Variable
        l_variable = wx.StaticText(dialog, label=l_variable)
        t_variable = wx.TextCtrl(dialog, value=variable)
        dialog.variable = t_variable
        dialog.top.Add(l_variable)
        dialog.top.Add(t_variable)

        # Error
        l_error = wx.StaticText(dialog, label=l_error)
        t_error = wx.TextCtrl(dialog, value=error)
        dialog.error = t_error
        dialog.top.Add(l_error)
        dialog.top.Add(t_error)

    def complete(self, dialog):
        """The user pressed 'ok' in the dialog."""
        variable = dialog.variable.GetValue()
        empty_variable = self.t("empty_variable",
                "The variable name is empty.  Which variable to check?")

        if not variable:
            wx.MessageBox(empty_variable, t("ui.message.error"),
                    wx.OK | wx.ICON_ERROR)
            dialog.variable.SetFocus()
            return None

        error = dialog.error.GetValue()

        arguments = (variable, error)
        return arguments
