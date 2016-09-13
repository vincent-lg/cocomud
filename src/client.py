"""This file contains the client that can connect to a MUD.

It is launched in a new thread, so as not to block the main thread.

"""

import re
from telnetlib import Telnet, WONT, WILL, ECHO
import threading
import time

try:
    from UniversalSpeech import say, braille
except ImportError:
    say = None
    braille = None

# Constants
ANSI_ESCAPE = re.compile(r'\x1b[^m]*m')

class Client(threading.Thread):

    """Class to receive data from the MUD."""

    def __init__(self, host, port=4000, timeout=0.1, engine=None):
        """Connects to the MUD."""
        threading.Thread.__init__(self)
        self.client = None
        self.timeout = timeout
        self.engine = engine
        self.running = False

        # Try to connect to the specified host and port
        self.client = Telnet(host, port)
        self.running = True

    def run(self):
        """Run the thread."""
        while self.running:
            time.sleep(self.timeout)
            msg = self.client.read_very_eager()
            if msg:
                self.handle_message(msg)

    def handle_message(self, msg):
        """When the client receives a message."""
        pass


class GUIClient(Client):

    """Client specifically linked to a GUI window.

    This client proceeds to send the text it receives to the frame.

    """

    def __init__(self, host, port=4000, timeout=0.1, engine=None):
        Client.__init__(self, host, port, timeout, engine)
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
        window.client = self.client

    def handle_message(self, msg):
        """When the client receives a message."""
        msg = msg.decode("utf-8", "replace")
        msg = ANSI_ESCAPE.sub('', msg)
        if self.window:
            self.window.handle_message(msg)

        # In any case, tries to find the TTS
        if self.engine.TTS_on:
            if say and braille:
                say(msg, interrupt=False)
                braille(msg)

    def handle_option(self, socket, command, option):
        """Handle a received option."""
        name = ""
        if command == WILL and option == ECHO:
            name = "hide"
        elif command == WONT and option == ECHO:
            name = "show"

        if name and self.window:
            self.window.handle_option(name)
