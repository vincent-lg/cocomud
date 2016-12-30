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

"""Module containing the notepad dialog."""

import wx

from ytranslate import t

class NotepadDialog(wx.Dialog):

    """Dialog for world and character notepad."""

    def __init__(self, notepad):
        wx.Dialog.__init__(self, None,
                title=t("ui.message.notepad.title"))
        self.notepad = notepad
        self.InitUI()
        self.Maximize()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Create the dialog
        self.text = wx.TextCtrl(self, size=(600, 400),
                style=wx.TE_MULTILINE)
        self.text.SetValue(self.notepad.content)
        sizer.Add(self.text)

        # Event binding
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.text.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def OnClose(self, e):
        """Close the dialog and save the notepad."""
        self.notepad.content = self.text.GetValue()
        self.notepad.save()
        self.Destroy()

    def OnKeyDown(self, e):
        """A key is pressed in the dialog."""
        if e.GetKeyCode() == wx.WXK_ESCAPE:
            self.Close()
        else:
            e.Skip()
