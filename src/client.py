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

"""This file contains the client that can connect to a MUD.

It is launched in a new thread, so as not to block the main thread.

"""

import os
import re
from telnetlib import Telnet, WONT, WILL, ECHO
import threading
import time

from screenreader import ScreenReader
from sharp.engine import SharpScript

# Constants
ANSI_ESCAPE = re.compile(r'\x1b[^m]*m')

class Client(threading.Thread):

    """Class to receive data from the MUD."""

    def __init__(self, host, port=4000, timeout=0.1, engine=None,
            world=None):
        """Connects to the MUD."""
        threading.Thread.__init__(self)
        self.client = None
        self.host = host
        self.port = port
        self.timeout = timeout
        self.engine = engine
        self.world = world
        self.running = False
        self.sharp_engine = SharpScript(engine, self, world)

    def disconnect(self):
        """Disconnect, close the client."""
        if self.client and self.client.get_socket():
            self.client.close()

        self.running = False

    def run(self):
        """Run the thread."""
        # Try to connect to the specified host and port
        self.client = Telnet(self.host, self.port)
        self.running = True
        while self.running:
            time.sleep(self.timeout)
            if not self.client.get_socket():
                break

            try:
                msg = self.client.read_very_eager()
            except EOFError:
                break

            if msg:
                for line in msg.splitlines():
                    for trigger in self.world.triggers:
                        trigger.feed(line)

                self.handle_message(msg)

        # Consider the thread as stopped
        self.running = False

        # If there's still an open window
        if self.window:
            self.window.handle_disconnection()

    def handle_message(self, msg, force_TTS=False, screen=True,
            speech=True, braille=True):
        """When the client receives a message.

        Parameters
            msg: the text to be displayed (str)
            force_TTS: should the text be spoken regardless?
            screen: should the text appear on screen?
            speech: should the speech be enabled?
            braille: should the braille be enabled?

        """
        pass

    def write(self, text, alias=True):
        """Write text to the client."""
        if text.startswith("#"):
            self.sharp_engine.execute(text)
        else:
            # Test the aliases
            if alias:
                for alias in self.world.aliases:
                    if alias.test(text):
                        return

            if not text.endswith("\r\n"):
                text += "\r\n"
            self.client.write(text)


class GUIClient(Client):

    """Client specifically linked to a GUI window.

    This client proceeds to send the text it receives to the frame.

    """

    def __init__(self, host, port=4000, timeout=0.1, engine=None,
            world=None):
        Client.__init__(self, host, port, timeout, engine, world)
        self.window = None
        if self.client:
            self.client.set_option_negotiation_callback(self.handle_option)

    def link_window(self, window):
        """Link to a window (a GUI object).

        This objectt can be of various types.  The client only interacts
        with it in two ways:  First, whenever it receives a message,
        it sends it to the window's 'handle_message' method.  It also
        calls the window's 'handle_option' method whenever it receives
        a Telnet option that it can recognize.

        """
        self.window = window
        window.client = self

    def handle_message(self, msg, force_TTS=False, screen=True,
            speech=True, braille=True):
        """When the client receives a message.

        Parameters
            msg: the text to be displayed (str)
            force_TTS: should the text be spoken regardless?
            screen: should the text appear on screen?
            speech: should the speech be enabled?
            braille: should the braille be enabled?

        """
        encoding = self.engine.settings["options.general.encoding"]
        msg = msg.decode(encoding, "replace")
        msg = ANSI_ESCAPE.sub('', msg)
        if self.window and screen:
            self.window.handle_message(msg)

        # In any case, tries to find the TTS
        if self.engine.TTS_on or force_TTS:
            # If outside of the window
            tts = False
            panel = self.window
            window = getattr(panel, "window", None)
            focus = (window.focus and panel.focus) if panel else False
            outside = (not window.focus and panel.focus) if panel else False
            if force_TTS:
                tts = True
            elif focus:
                tts = True
            elif outside and self.engine.settings["options.TTS.outside"]:
                tts = True

            if tts:
                ScreenReader.talk(msg, speech=speech, braille=braille)

    def handle_option(self, socket, command, option):
        """Handle a received option."""
        name = ""
        if command == WILL and option == ECHO:
            name = "hide"
        elif command == WONT and option == ECHO:
            name = "show"

        if name and self.window:
            self.window.handle_option(name)
