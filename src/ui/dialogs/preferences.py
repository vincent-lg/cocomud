"""Module containing the preferences dialog."""

import wx

class TTSTab(wx.Panel):

    """TTS tab."""

    def __init__(self, parent, engine):
        super(TTSTab, self).__init__(parent)
        self.engine = engine

        self.InitUI()
        self.Fit()

    def InitUI(self):
        settings = self.engine.settings
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(15, 15)
        panel.SetSizer(sizer)

        # TTS preferendces
        self.TTS_on = wx.CheckBox(panel, label="Enable TTS (Text-To Speech)")
        self.TTS_on.SetValue(settings["options.TTS.on"])
        self.TTS_outside = wx.CheckBox(panel, label="Enable TTS when on a different window")
        self.TTS_outside.SetValue(settings["options.TTS.outside"])

        # Append to the sizer
        sizer.Add(self.TTS_on, pos=(0, 0))
        sizer.Add(self.TTS_outside, pos=(0, 1))


class PreferencesTabs(wx.Notebook):

    """Preference tabs."""

    def __init__(self, parent, engine):
        wx.Notebook.__init__(self, parent)

        TTS_tab = TTSTab(self, engine)
        self.AddPage(TTS_tab, "TTS")
        self.TTS = TTS_tab

class PreferencesDialog(wx.Dialog):

    """Preferences dialog."""

    def __init__(self, engine):
        super(PreferencesDialog, self).__init__(None, title="Preferences")
        self.engine = engine

        self.InitUI()
        self.Maximize()

    def InitUI(self):
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(15, 15)
        panel.SetSizer(sizer)

        # Add the tabs
        self.tabs = PreferencesTabs(panel, self.engine)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)

        # Append to the sizer
        sizer.Add(self.tabs, pos=(1, 0), span=( 5, 5))
        sizer.Add(buttons, pos=(8, 0), span=(1, 2))

        # Event binding
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

    def OnOK(self, e):
        """Save the preferences."""
        settings = self.engine.settings
        tts = self.tabs.TTS
        settings["options.TTS.on"] = tts.TTS_on.GetValue()
        settings["options.TTS.outside"] = tts.TTS_outside.GetValue()
        settings["options"].write()
        self.Destroy()

    def OnCancel(self, e):
        """Simply exit the dialog."""
        self.Destroy()
