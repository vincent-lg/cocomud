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

from ytranslate import t

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

    def display(self, dialog, text="", screen=True, speech=True, braille=True):
        """Display the function's argument."""
        l_text = self.t("text", "Text to be displayed and sent")
        l_screen = self.t("screen", "Display the message in the client")
        l_speech = self.t("speech", "Speak the message aloud")
        l_braille = self.t("braille", "Display the message on the Braille display")

        # Dialog
        l_text = wx.StaticText(dialog, label=l_text)
        t_text = wx.TextCtrl(dialog, value=text,
                style=wx.TE_MULTILINE)
        dialog.text = t_text
        dialog.top.Add(l_text)
        dialog.top.Add(t_text)

        # Checkboxes
        options = wx.BoxSizer(wx.HORIZONTAL)
        dialog.cb_screen = wx.CheckBox(dialog, label=l_screen)
        dialog.cb_screen.SetValue(screen)
        dialog.cb_speech = wx.CheckBox(dialog, label=l_speech)
        dialog.cb_speech.SetValue(speech)
        dialog.cb_braille = wx.CheckBox(dialog, label=l_braille)
        dialog.cb_braille.SetValue(braille)
        options.Add(dialog.cb_screen)
        options.Add(dialog.cb_speech)
        options.Add(dialog.cb_braille)
        dialog.top.Add(options)

    def complete(self, dialog):
        """The user pressed 'ok' in the dialog."""
        text = dialog.text.GetValue().encode("utf-8", "replace")
        empty_text = self.t("empty_text",
                "The text field is empty.  What should I say?")
        if not text:
            wx.MessageBox(empty_text, t("ui.message.error"),
                    wx.OK | wx.ICON_ERROR)
            dialog.text.SetFocus()
            return None

        arguments = [text]
        # Get the options
        screen = dialog.cb_screen.GetValue()
        speech = dialog.cb_speech.GetValue()
        braille = dialog.cb_braille.GetValue()
        if not screen:
            arguments.append("-screen")
        if not speech:
            arguments.append("-speech")
        if not braille:
            arguments.append("-braille")

        return tuple(arguments)
