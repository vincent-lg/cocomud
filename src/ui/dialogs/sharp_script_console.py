# Copyright (c) 2016-2020, LE GOFF Vincent
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

"""This file contains the SharpScriptConsoleDialog."""

import sys
import threading
import time
import traceback

from accesspanel import AccessPanel
import wx
from ytranslate.tools import t

from log import ui as logger
from screenreader import ScreenReader

class SharpScriptConsolePanel(AccessPanel):

    def __init__(self, parent, session):
        AccessPanel.__init__(self, parent, history=True, lock_input=True)
        self.output.SetDefaultStyle(wx.TextAttr(wx.WHITE, wx.BLACK))
        self.session = session
        self.lines = []

        # Event binding
        self.output.Bind(wx.EVT_TEXT_PASTE, self.OnPaste)

        # Launch the console
        logger.debug("Starting the SharpScript console")
        self.Send(t("ui.dialog.sharp_script_console.banner"))

    def OnInput(self, message):
        """Some text has been sent from the input."""
        # Either send the buffer to the SharpScript engine or wait for a new line
        self.lines.append(message)
        execute = True
        if len(self.lines) == 1:
            if any(message.endswith(block) for block in ("{", "{+", "(")):
                # An opening block has been detected
                execute = False
        else:
            if message not in (")", "}"):
                execute = False

        if execute:
            buffer = "\n".join(self.lines)
            if self.session and self.session.engine:
                engine = self.session.engine
                sharp_engine = self.session.sharp_engine
                self.Send("+ " + "+ ".join(self.lines))

                # Save the TTS_on and TTS_outside, turn them on temporarily
                engine.TTS_on = True
                engine.TTS_outside = True
                engine.redirect_message = self.Send
                try:
                    sharp_engine.execute(buffer)
                except Exception:
                    error = t("ui.dialog.sharp_script_console.error") + "\n"
                    error += traceback.format_exc().strip()
                    self.Send(error)
                finally:
                    self.lines[:] = []

    def OnPaste(self, e):
        """Paste several lines in the input field.

        This event simply sends this text to be processed.

        """
        clipboard = wx.TextDataObject()
        success = wx.TheClipboard.GetData(clipboard)
        if success:
            clipboard = clipboard.GetText()
            input = self.input + clipboard
            if input.endswith("\n"):
                lines = input.splitlines()
                for line in lines:
                    self.OnInput(line)
                self.ClearInput()
            else:
                e.Skip()


class SharpScriptConsoleDialog(wx.Dialog):

    def __init__(self, session):
        wx.Dialog.__init__(self, None, title=t("ui.dialog.sharp_script_console.title"))
        self.session = session

        # Build the dialog
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Add in the panel
        self.panel = SharpScriptConsolePanel(self, session)
        self.TTS_on = session.engine.TTS_on
        self.TTS_outside = session.engine.TTS_outside

        # Finish designing the window
        sizer.Add(self.panel)
        sizer.Fit(self)

        # Event binding
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, e):
        """Close the console."""
        self.session.engine.TTS_on = self.TTS_on
        self.session.engine.TTS_outside = self.TTS_outside
        self.session.engine.redirect_message = None
        if self.session and self.session.world:
            self.session.world.save()

        self.Destroy()
