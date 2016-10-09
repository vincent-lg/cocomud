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

"""Module containing the Say function class."""

import wx

from sharp import Function

class Say(Function):

    """Function SharpScript 'say'.

    This function expects an argument as a parameter and sends it
    to the screen reader and Braille display if supported.

    """

    description = "Say a message"

    def run(self, text, screen=True, speech=True, braille=True):
        """Say the text."""
        if self.client:
            self.client.handle_message(text, screen=screen,
                    speech=speech, braille=braille)

    def display(self, dialog, text=""):
        """Display the function's argument."""
        l_text = wx.StaticText(dialog, label="Text to be said")
        t_text = wx.TextCtrl(dialog, value=text,
                style=wx.TE_MULTILINE)
        dialog.text = t_text
        dialog.top.Add(l_text)
        dialog.top.Add(t_text)

    def complete(self, dialog):
        """The user pressed 'ok' in the dialog."""
        text = dialog.text.GetValue().encode("utf-8", "replace")
        if not text:
            wx.MessageBox("The 'text' field is empty.  What should I say?",
                    "Error", wx.OK | wx.ICON_ERROR)
            dialog.text.SetFocus()
            return None

        return (text, )
