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

"""This file contains the client that can connect to a MUD.

Starting from CocoMUD 45, the network is handled by Twisted.  The
Client class inherits from 'twisted.conch.telnet.Telnet', which
already handles a great deal of the Telnet protocol.

"""

import os
from random import randint
import re
import socket
from telnetlib import Telnet, WONT, WILL, ECHO, NOP, AYT, IAC, GA
import threading
import time

from twisted.internet import reactor
from twisted.internet.error import ConnectionDone
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.conch.telnet import Telnet
import wx
from wx.lib.pubsub import pub

from log import logger
from screenreader import ScreenReader
from screenreader import ScreenReader

# Constants
ANSI_ESCAPE = re.compile(r'\x1b[^m]*m')

class Client(Telnet):

    """Class to receive data from the MUD using a Telnet protocol."""

    def disconnect(self):
        """Disconnect, close the client."""
        if self.transport:
            self.transport.loseConnection()

        self.running = False

    def connectionMade(self):
        """Established connection, send the differed commands."""
        self.has_GA = False
        self.queue = b""
        self.defer = None
        self.anti_idle = None
        host = self.transport.getPeer().host
        port = self.transport.getPeer().port
        log = logger("client")
        log.info("Connected to {host}:{port}".format(
                host=host, port=port))
        # Record commands
        self.commandMap[GA] = self.handle_GA

        self.factory.resetDelay()
        for command in self.factory.commands:
            self.transport.write(command.encode() + b"\r\n")

        self.factory.stopTrying()

    def connectionLost(self, reason):
        """The connection was lost."""
        self.send_queue()
        host = self.transport.getPeer().host
        port = self.transport.getPeer().port
        log = logger("client")
        log.info("Lost Connection on {host}:{port}: {reason}".format(
                host=host, port=port, reason=reason.type))
        wx.CallAfter(pub.sendMessage, "disconnect", client=self,
                reason=reason)
        if reason.type is ConnectionDone:
            self.factory.stopTrying()

    def applicationDataReceived(self, data):
        """Receive something."""
        if self.has_GA:
            self.queue += data
            if self.defer:
                self.defer.cancel()
            self.defer = reactor.callLater(0.2, self.send_queue)
        else:
            if self.queue:
                data = self.queue + b"\r\n" + data
                self.queue = b""

            # Cancel the deferred, if exists
            if self.defer:
                self.defer.cancel()
                self.defer = None

            encoding = self.factory.engine.settings["options.general.encoding"]
            msg = data.decode(encoding, errors="replace")
            with self.factory.world.lock:
                self.handle_lines(msg)

    def send_queue(self):
        old_GA = self.has_GA
        self.has_GA = False
        self.defer = None
        if self.queue:
            queue = self.queue
            self.queue = b""
            self.applicationDataReceived(queue)
        self.has_GA = old_GA

    def handle_GA(self, *args, **kwargs):
        """Handle the Telnet Go-Ahead."""
        self.has_GA = False
        if self.queue:
            queue = self.queue
            self.queue = b""
            self.applicationDataReceived(queue)
        self.has_GA = True

    def reverse_anti_idle(self, verbose=False, to_panel=False):
        """Reverse anti-idle."""
        if self.anti_idle:
            # Terminate
            if verbose:
                self.handle_message("Anti idle off.")
            self.anti_idle.cancel()
            self.anti_idle = None
            if to_panel:
                self.factory.panel.window.gameMenu.Check(
                        self.factory.panel.window.chk_anti_idle.GetId(), False)
        else:
            # Begin anti idle
            if verbose:
                self.handle_message("Anti idle on.")
            self.anti_idle = reactor.callLater(1, self.keep_anti_idle)
            if to_panel:
                self.factory.panel.window.gameMenu.Check(
                        self.factory.panel.window.chk_anti_idle.GetId(), True)

    def keep_anti_idle(self):
        """Keep the anti-idle active."""
        self.transport.write(b"\r\n")
        next_time = randint(900, 1200)
        next_time += randint(1, 100) / 100
        self.anti_idle = reactor.callLater(next_time, self.keep_anti_idle)

    def run(self):
        """Run the thread."""
        # Try to connect to the specified host and port
        host = self.factory.world.hostname
        port = self.factory.world.port
        protocol = self.factory.world.protocol.lower()
        protocol = "SSL" if protocol == "ssl" else "telnet"
        log = logger("client")
        log.info("Connecting {protocol} client for {host}:{port}".format(
                protocol=protocol, host=host, port=port))
        self.running = True

    def handle_lines(self, msg):
        """Handle multiple lines of text."""
        mark = None
        lines = []
        no_ansi_lines = []

        # Line breaks are different whether rich text is used or not
        if self.factory.panel and self.factory.panel.rich:
            nl = "\n"
        else:
            nl = "\r\n"

        for line in msg.splitlines():
            no_ansi_line = ANSI_ESCAPE.sub('', line)
            display = True
            matches = []
            for trigger in self.factory.world.triggers:
                trigger.sharp_engine = self.factory.sharp_engine
                try:
                    match = trigger.test(no_ansi_line)
                except Exception:
                    log = logger("client")
                    log.exception("The trigger {} failed".format(
                            repr(trigger.reaction)))
                else:
                    if match:
                        matches.append((trigger, match))

            if matches:
                if len(matches) > 1:
                    matches.sort(
                        key=lambda c: len(c[0].reaction), reverse=True
                    )

                trigger, match = matches[0]
                trigger.set_variables(match)
                try:
                    trigger.execute()
                except Exception:
                    log = logger("client")
                    log.exception("The trigger {} failed execution".format(
                            repr(trigger.reaction)))

                if trigger.mute:
                    display = False
                if trigger.mark and mark is None:
                    before = nl.join([l for l in no_ansi_lines])
                    mark = len(before) + len(nl)

                # Handle triggers with substitution
                if trigger.substitution:
                    display = False
                    replacement = trigger.replace()
                    lines.extend(replacement.splitlines())

            if display:
                if self.factory.strip_ansi:
                    lines.append(no_ansi_line)
                else:
                    lines.append(line)

                if no_ansi_line.strip():
                    no_ansi_lines.append(no_ansi_line)

        # Handle the remaining text
        try:
            lines = [l for l in lines if l]
            self.handle_message("\r\n".join(lines), mark=mark)
        except Exception:
            log = logger("client")
            log.exception(
                    "An error occurred when handling a message")

    def handle_message(self, msg, force_TTS=False, screen=True,
            speech=True, braille=True, mark=None):
        """When the client receives a message.

        Args:
            msg: the text to be displayed (str)
            force_TTS: should the text be spoken regardless?
            screen: should the text appear on screen?
            speech: should the speech be enabled?
            braille: should the braille be enabled?
            mark: the index where to move the cursor.

        """
        no_ansi_msg = ANSI_ESCAPE.sub('', msg)
        self.factory.session.log_message(no_ansi_msg)
        if screen:
            if self.factory.engine.redirect_message:
                self.factory.engine.redirect_message(msg)
            else:
                wx.CallAfter(pub.sendMessage, "message", client=self,
                    message=msg, mark=mark)

        # In any case, tries to find the TTS
        panel = self.factory.panel
        if self.factory.engine.TTS_on or force_TTS:
            # If outside of the window
            tts = False
            if force_TTS:
                tts = True
            elif panel.inside and panel.focus:
                tts = True
            elif not panel.inside and panel.engine.TTS_outside:
                tts = True

            if tts:
                interrupt = self.factory.engine.settings[
                        "options.TTS.interrupt"]
                ScreenReader.talk(no_ansi_msg, speech=speech, braille=braille,
                        interrupt=interrupt)

    def write(self, text, alias=True):
        """Write text to the client."""
        self.factory.session.log_command(text)
        # Break in chunks based on the command stacking, if active
        settings = self.factory.engine.settings
        stacking = settings["options.input.command_stacking"]
        encoding = settings["options.general.encoding"]
        chunks = [text]
        if stacking:
            delimiter = re.escape(stacking)
            re_stacking = u"(?<!{s}){s}(?!{s})".format(s=delimiter)
            re_del = re.compile(re_stacking, re.UNICODE)
            chunks = re_del.split(text)

            # Reset ;; as ; (or other command stacking character)
            def reset_del(match):
                return match.group(0)[1:]

            for i, chunk in enumerate(chunks):
                chunks[i] = re.sub(delimiter + "{2,}", reset_del, chunk)

        with self.factory.world.lock:
            for text in chunks:
                # Test the aliases
                if alias:
                    for alias in self.factory.world.aliases:
                        alias.sharp_engine = self.factory.sharp_engine
                        if alias.test(text):
                            return

                if not text.endswith("\r\n"):
                    text += "\r\n"

                self.transport.write(text.encode(encoding, errors="replace"))

    def test_macros(self, key, modifiers):
        """Test the macros of this world."""
        found = False
        with self.factory.world.lock:
            for macro in self.factory.world.macros:
                code = (macro.key, macro.modifiers)
                macro.sharp_engine = self.factory.sharp_engine
                if code == (key, modifiers):
                    macro.execute(self.factory.engine, self)
                    found = True
                    break

        return found


class CocoFactory(ReconnectingClientFactory):

    """Factory used by CocoMUD client to generate Telnet clients."""

    def __init__(self, world, session, panel):
        self.world = world
        self.session = session
        self.panel = panel
        self.engine = world.engine
        self.sharp_engine = session.sharp_engine
        self.commands = []
        self.strip_ansi = False

    def buildProtocol(self, addr):
        client = Client()
        client.factory = self
        client.run()
        self.panel.client = client
        self.sharp_engine.bind_client(client)
        return client
