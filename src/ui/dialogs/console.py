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

"""This file contains the ConsoleDialog."""

from __future__ import absolute_import
from code import InteractiveConsole
import sys
import threading
import time

from accesspanel import AccessPanel
import wx
from ytranslate.tools import t

from log import ui as logger
from screenreader import ScreenReader

class CocoIC(InteractiveConsole):

    """Class to extend the basic InteractiveConsole."""

    def __init__(self, panel):
        InteractiveConsole.__init__(self)
        self.to_exec = None
        self.panel = panel
        self.interrupt = False

    def interact(self, banner=None):
        """Interact and redirect to self.write."""
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "
        cprt = 'Type "help", "copyright", "credits" or "license" for more information.'
        logger.debug(u"Sending the welcome prompt")
        if banner is None:
            self.write("Python %s on %s\n%s\n" %
                       (sys.version, sys.platform, cprt))
        else:
            self.write("%s\n" % str(banner))

        # Display the prompt
        self.panel.Send(">>>")

        more = 0
        while 1:
            if self.interrupt:
                break

            try:
                if more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                try:
                    line = self.raw_input()
                    if line is None:
                        time.sleep(0.2)
                        continue

                    encoding = "utf-8"
                    line = line.decode(encoding, errors="replace")
                except EOFError:
                    self.write("\n")
                    break
                else:
                    stdout = sys.stdout
                    stderr = sys.stderr
                    sys.stdout = self
                    sys.stderr = self
                    logger.debug(u"Executing {}".format(repr(line)))
                    more = self.push(line)
                    sys.stdout = stdout
                    sys.stderr = stderr
                    logger.debug("Exec successful")

                    # Display the prompt
                    if more:
                        prompt = sys.ps2
                    else:
                        prompt = sys.ps1

                    self.panel.Send(prompt)
            except KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
                self.resetbuffer()
                more = 0

    def raw_input(self):
        """Write a prompt and read a line."""
        if self.to_exec is not None:
            lines = self.to_exec.splitlines()
            if not lines:
                line = ""
                self.to_exec = None
            else:
                line = lines[0]
                self.to_exec = "\n".join(lines[1:]) if len(lines) > 1 else None

            return line

        return None

    def write(self, message):
        """Write the text to the interface."""
        message = message.decode("utf-8", errors="replace")
        logger.debug(u"Received in answer {}".format(repr(message)))
        self.panel.Send(message)


class GUIThread(threading.Thread):

    """A thread between the GUI and the console."""

    def __init__(self, panel):
        threading.Thread.__init__(self)
        self.panel = panel
        self.console = CocoIC(self.panel)

    def run(self):
        self.panel.Send(t("ui.dialog.console.warning"))
        self.console.interact()
        logger.debug(u"Begin interacting with the Python console")


class ConsolePanel(AccessPanel):

    def __init__(self, parent, engine, world=None, panel=None):
        AccessPanel.__init__(self, parent, history=True, lock_input=True)
        self.output.SetDefaultStyle(wx.TextAttr(wx.WHITE, wx.BLACK))
        self.engine = engine
        self.world = world
        self.panel = panel
        self.thread = GUIThread(self)
        self.locals = {
            "engine": self.engine,
            "world": self.world,
            "panel": self.panel,
        }

        # Event binding
        self.output.Bind(wx.EVT_TEXT_PASTE, self.OnPaste)

        # Launch the console
        self.thread.console.locals = self.locals
        self.thread.start()
        logger.debug(u"Starting the Python console thread")

    def OnInput(self, message):
        """Some text has been sent from the input."""
        # Converts the text back to 'str'
        message = message.encode("utf-8", errors="replace")
        logger.debug(u"Received {}".format(repr(message)))
        self.thread.console.to_exec = message

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


class ConsoleDialog(wx.Dialog):

    def __init__(self, engine, world=None, panel=None):
        wx.Dialog.__init__(self, None, title=t("ui.dialog.console.title"))
        self.engine = engine
        self.world = world

        # Build the dialog
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Add in the panel
        logger.debug("Creating the Python console")
        self.panel = ConsolePanel(self, engine, world, panel)

        # Finish designing the window
        sizer.Add(self.panel)
        sizer.Fit(self)

        # Event binding
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, e):
        """Close the console."""
        self.panel.thread.console.interrupt = True
        self.Destroy()
