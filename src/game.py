"""This file contains the GameEngine class."""

from client import GUIClient
from config import Settings

class GameEngine:

    """A class representing the game engine.

    An instance of this class is to be created each time the program
    runs.  It doesn't handle thegraphical user interface, but centralizes
    about anything else:  the main configuration, world configuration
    of different games, aliases, macros, triggers and so on.  The
    GUI has a direct access to the engine and can therefore access it.

    """

    def __init__(self):
        self.settings = Settings()

    def load(self):
        """Load the configuration."""
        self.settings.load()
        self.TTS_on = self.settings["options.TTS.on"]
        self.TTS_outside = self.settings["options.TTS.outside"]

    def open(self, host, port):
        """Connect to the specified host and port.

        This method creates and returns a 'GUIClient' class initialized
        with the specified information.

        """
        client = GUIClient("vanciamud.fr", 4000, engine=self)
        return client