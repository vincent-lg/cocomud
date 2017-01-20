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
import socket
from telnetlib import Telnet, WONT, WILL, ECHO, NOP, AYT, IAC
import threading
import time

from log import logger
from screenreader import ScreenReader

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
        self.strip_ansi = False
        self.commands = []
        self.sharp_engine = None

    def disconnect(self):
        """Disconnect, close the client."""
        if self.client and self.client.get_socket():
            self.client.close()

        self.running = False

    def pre_run(self):
        """Method called before running."""
        pass

    def run(self):
        """Run the thread."""
        # Try to connect to the specified host and port
        self.client = Telnet(self.host, self.port)
        self.running = True
        self.pre_run()

        # If the client has commands
        for command in self.commands:
            self.client.write(command + "\r\n")

        while self.running:
            time.sleep(self.timeout)
            encoding = self.engine.settings["options.general.encoding"]
            if not self.client.get_socket():
                break

            try:
                msg = self.client.read_very_eager()
            except socket.error:
                if self.window:
                    self.window.handle_reconnection()
            except EOFError:
                break

            if msg:
                msg = msg.decode(encoding, errors="replace")
                with self.world.lock:
                    self.handle_lines(msg)

        # Consider the thread as stopped
        self.running = False

        # If there's still an open window
        if self.window:
            self.window.handle_disconnection()

    def handle_lines(self, msg):
        """Handle multiple lines of text."""
        mark = None
        lines = []
        no_ansi_lines = []
        triggers = []
        for line in msg.splitlines():
            no_ansi_line = ANSI_ESCAPE.sub('', line)
            display = True
            for trigger in self.world.triggers:
                trigger.sharp_engine = self.sharp_engine
                try:
                    match = trigger.test(no_ansi_line)
                except Exception:
                    log = logger("client")
                    log.exception("The trigger {} failed".format(
                            repr(trigger.readction)))
                else:
                    if match:
                        triggers.append((trigger, match, no_ansi_line))
                        if trigger.mute:
                            display = False
                        if trigger.mark and mark is None:
                            before = "\n".join([l for l in no_ansi_lines])
                            mark = len(before) + 1

                        # Handle triggers with substitution
                        if trigger.substitution:
                            display = False
                            trigger.set_variables(match)
                            replacement = trigger.replace()
                            lines.extend(replacement.splitlines())

            if display:
                if self.strip_ansi:
                    lines.append(no_ansi_line)
                else:
                    lines.append(line)

                if no_ansi_line.strip():
                    no_ansi_lines.append(no_ansi_line)

        # Handle the remaining text
        try:
            liens = [l for l in lines if l]
            self.handle_message("\r\n".join(lines), mark=mark)
        except Exception:
            log = logger("client")
            log.exception(
                    "An error occurred when handling a message")

        # Execute the triggers
        for trigger, match, line in triggers:
            trigger.set_variables(match)
            trigger.execute()

    def handle_message(self, msg, force_TTS=False, screen=True,
            speech=True, braille=True, mark=None):
        """When the client receives a message.

        Parameters
            msg: the text to be displayed (str)
            force_TTS: should the text be spoken regardless?
            screen: should the text appear on screen?
            speech: should the speech be enabled?
            braille: should the braille be enabled?
            mark: the index on which to move the cursor

        """
        pass

    def write(self, text, alias=True):
        """Write text to the client."""
        if text.startswith("#"):
            self.sharp_engine.execute(text)
        else:
            # Break in chunks based on the command stacking, if active
            settings = self.engine.settings
            stacking = settings["options.input.command_stacking"]
            encoding = settings["options.general.encoding"]
            if stacking:
                delimiter = re.escape(stacking)
                re_del = re.compile("(?<!{s}){s}(?!{s})".format(s=delimiter), re.UNICODE)
                chunks = re_del.split(text)

                # Reset ;; as ; (or other command stacking character)
                def reset_del(match):
                    return match.group(0)[1:]

                for i, chunk in enumerate(chunks):
                    chunks[i] = re.sub(delimiter + "{2,}", reset_del, chunk)
                    if isinstance(chunks[i], unicode):
                        chunks[i] = chunks[i].encode(encoding,
                                errors="replace")
            else:
                chunks = [text.encode(encoding, "replace")]

            with self.world.lock:
                for text in chunks:
                    # Test the aliases
                    if alias:
                        for alias in self.world.aliases:
                            alias.sharp_engine = self.sharp_engine
                            if alias.test(text):
                                return

                if not text.endswith("\r\n"):
                    text += "\r\n"

                self.client.write(text)

    def test_macros(self, key, modifiers):
        """Test the macros of this world."""
        found = False
        with self.world.lock:
            for macro in self.world.macros:
                code = (macro.key, macro.modifiers)
                macro.sharp_engine = self.sharp_engine
                if code == (key, modifiers):
                    macro.execute(self.engine, self)
                    found = True
                    break

        return found



class GUIClient(Client):

    """Client specifically linked to a GUI window.

    This client proceeds to send the text it receives to the frame.

    """

    def __init__(self, host, port=4000, timeout=0.1, engine=None,
            world=None):
        Client.__init__(self, host, port, timeout, engine, world)
        self.window = None

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

    def pre_run(self):
        """Method called before running."""
        self.client.set_option_negotiation_callback(self.handle_option)

    def handle_message(self, msg, force_TTS=False, screen=True,
            speech=True, braille=True, mark=None):
        """When the client receives a message.

        Parameters
            msg: the text to be displayed (str)
            force_TTS: should the text be spoken regardless?
            screen: should the text appear on screen?
            speech: should the speech be enabled?
            braille: should the braille be enabled?
            mark: the index where to move the cursor.

        """
        if self.window and screen:
            self.window.handle_message(msg, mark)

        # In any case, tries to find the TTS
        msg = ANSI_ESCAPE.sub('', msg)
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
                interrupt = self.engine.settings["options.TTS.interrupt"]
                ScreenReader.talk(msg, speech=speech, braille=braille,
                        interrupt=interrupt)

    def handle_option(self, socket, command, option):
        """Handle a received option."""
        name = ""
        if command == AYT:
            log = logger("client")
            log.debug("Received a AYT, replying with a NOP.")
            socket.send(IAC + NOP)
        elif command == WILL and option == ECHO:
            name = "hide"
        elif command == WONT and option == ECHO:
            name = "show"
