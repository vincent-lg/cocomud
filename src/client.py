"""This file contains the client that can connect to a MUD.

It is launched in a new thread, so as not to block the main thread.

"""

import re
from telnetlib import Telnet, WONT, WILL, ECHO
import threading
import time
import wx

try:
    from UniversalSpeech import say, braille
except ImportError:
    say = None
    braille = None

from ui.event import FocusEvent, myEVT_FOCUS

# Constants
ANSI_ESCAPE = re.compile(r'\x1b[^m]*m')

class Client(threading.Thread):

    """Class to receive data from the MUD."""

    def __init__(self, host, port=4000, timeout=0.1, settings=None):
        """Connects to the MUD."""
        threading.Thread.__init__(self)
        self.client = None
        self.timeout = timeout
        self.settings = settings
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

    def __init__(self, host, port=4000, timeout=0.1, panel=None,
            settings=None):
        Client.__init__(self, host, port, timeout, settings)
        self.panel = panel
        if self.client:
            self.client.set_option_negotiation_callback(self.handle_option)

    def handle_message(self, msg):
        """When the client receives a message."""
        pos = self.panel.output.GetInsertionPoint()
        msg = msg.decode("utf-8", "replace")
        msg = ANSI_ESCAPE.sub('', msg)
        self.panel.output.write(msg)
        self.panel.output.SetInsertionPoint(pos)
        if self.settings["options.TTS.on"]:
            if say and braille:
                say(msg, interrupt=False)
                braille(msg)

    def handle_option(self, socket, command, option):
        """Handle a received option."""
        if command == WILL and option == ECHO:
            evt = FocusEvent(myEVT_FOCUS, -1, "password")
            wx.PostEvent(self.panel, evt)
        elif command == WONT and option == ECHO:
            evt = FocusEvent(myEVT_FOCUS, -1, "input")
            wx.PostEvent(self.panel, evt)
