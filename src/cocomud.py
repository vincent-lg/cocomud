"""This demo file creates a simple client with TTS support."""

import wx

from ytranslate import init, select

init(root_dir="translations")

from game import GameEngine
from ui.window import ClientWindow

app = wx.App()
# Load the user configuration
engine = GameEngine()
engine.load()

# Select the configured language
lang = engine.settings.get_language()
select(lang)

# Create the client and ClientWindow
client = engine.open("vanciamud.fr", 4000)
window = ClientWindow(engine)
client.link_window(window)
client.start()
app.MainLoop()
