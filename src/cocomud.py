"""This demo file creates a simple client with TTS support."""

import wx

from client import GUIClient
from config import Settings
from ui.window import MainWindow

settings = Settings()
settings.load()
app = wx.App()
window = MainWindow(settings)
client = GUIClient("vanciamud.fr", 4000, 0.1, window.panel, settings)
window.panel.client = client.client
client.start()
app.MainLoop()
