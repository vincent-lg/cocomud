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

"""Module containing the preferences dialog."""

import wx

from ytranslate import t

class GeneralTab(wx.Panel):

    """General tab."""

    def __init__(self, parent, engine):
        super(GeneralTab, self).__init__(parent)
        self.engine = engine

        self.InitUI()
        self.Fit()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Language selection
        l_languages = wx.StaticText(self, label=t("ui.dialog.general"))
        languages = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        languages.InsertColumn(0, "Name")
        self.languages = languages
        self.PopulateList()

        # Append to the sizer
        sizer.Add(l_languages)
        sizer.Add(languages, proportion=4)

    def PopulateList(self):
        """Add the different languages in the list."""
        supported = self.engine.settings.LANGUAGES
        codes = [lang[0] for lang in supported]
        languages = [lang[1] for lang in supported]
        for language in languages:
            self.languages.Append((language, ))

        default = self.engine.settings.get_language()
        index = codes.index(default)
        self.languages.Select(index)
        self.languages.Focus(index)

    def get_selected_language(self):
        """Return the selected language's code."""
        supported = self.engine.settings.LANGUAGES
        codes = [lang[0] for lang in supported]
        languages = [lang[1] for lang in supported]
        index = self.languages.GetFirstSelected()
        return codes[index]


class DisplayTab(wx.Panel):

    """Display tab."""

    def __init__(self, parent, engine):
        super(DisplayTab, self).__init__(parent)
        self.engine = engine
        self.supported = [
            "ascii",
            "big5",
            "big5hkscs",
            "cp037",
            "cp424",
            "cp437",
            "cp500",
            "cp720",
            "cp737",
            "cp775",
            "cp850",
            "cp852",
            "cp855",
            "cp856",
            "cp857",
            "cp858",
            "cp860",
            "cp861",
            "cp862",
            "cp863",
            "cp864",
            "cp865",
            "cp866",
            "cp869",
            "cp874",
            "cp875",
            "cp932",
            "cp949",
            "cp950",
            "cp1006",
            "cp1026",
            "cp1140",
            "cp1250",
            "cp1251",
            "cp1252",
            "cp1253",
            "cp1254",
            "cp1255",
            "cp1256",
            "cp1257",
            "cp1258",
            "euc_jp",
            "euc_jis_2004",
            "euc_jisx0213",
            "euc_kr",
            "gb2312",
            "gbk",
            "gb18030",
            "hz",
            "iso2022_jp",
            "iso2022_jp_1",
            "iso2022_jp_2",
            "iso2022_jp_2004",
            "iso2022_jp_3",
            "iso2022_jp_ext",
            "iso2022_kr",
            "latin_1",
            "iso8859_2",
            "iso8859_3",
            "iso8859_4",
            "iso8859_5",
            "iso8859_6",
            "iso8859_7",
            "iso8859_8",
            "iso8859_9",
            "iso8859_10",
            "iso8859_13",
            "iso8859_14",
            "iso8859_15",
            "iso8859_16",
            "johab",
            "koi8_r",
            "koi8_u",
            "mac_cyrillic",
            "mac_greek",
            "mac_iceland",
            "mac_latin2",
            "mac_roman",
            "mac_turkish",
            "ptcp154",
            "shift_jis",
            "shift_jis_2004",
            "shift_jisx0213",
            "utf_32",
            "utf_32_be",
            "utf_32_le",
            "utf_16",
            "utf_16_be",
            "utf_16_le",
            "utf_7",
            "utf_8",
            "utf_8_sig"
        ]

        self.InitUI()
        self.Fit()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Encoding selection
        l_encodings = wx.StaticText(self, label=t("ui.dialog.encodings"))
        encodings = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        encodings.InsertColumn(0, "Name")
        self.encodings = encodings
        self.PopulateList()

        # Append to the sizer
        sizer.Add(l_encodings)
        sizer.Add(encodings, proportion=4)

    def PopulateList(self):
        """Add the different encodings in the list."""
        supported = self.supported
        for encoding in supported:
            self.encodings.Append((encoding, ))

        default = self.engine.settings["options.general.encoding"]
        try:
            index = supported.index(default)
        except IndexError:
            pass
        else:
            self.encodings.Select(index)
            self.encodings.Focus(index)

    def get_selected_encoding(self):
        """Return the selected encoding."""
        supported = self.supported
        index = self.encodings.GetFirstSelected()
        return supported[index]


class AccessibilityTab(wx.Panel):

    """Accessibility tab."""

    def __init__(self, parent, engine):
        super(AccessibilityTab, self).__init__(parent)
        self.engine = engine

        self.InitUI()
        self.Fit()

    def InitUI(self):
        settings = self.engine.settings
        sizer = wx.GridBagSizer(15, 15)
        self.SetSizer(sizer)

        # Tabbing
        self.tab_end = wx.CheckBox(self, label=t("ui.dialog.tab_end"))
        self.tab_end.SetValue(settings["options.accessibility.tab_end"])

        # Automatic NL at the end
        self.nl_end = wx.CheckBox(self, label=t("ui.dialog.nl_end"))
        self.nl_end.SetValue(settings["options.accessibility.nl_end"])

        # TTS preferendces
        self.TTS_on = wx.CheckBox(self, label=t("ui.dialog.TTS.on"))
        self.TTS_on.SetValue(settings["options.TTS.on"])
        self.TTS_outside = wx.CheckBox(self, label=t("ui.dialog.TTS.outside"))
        self.TTS_outside.SetValue(settings["options.TTS.outside"])

        # Append to the sizer
        sizer.Add(self.tab_end, pos=(0, 0))
        sizer.Add(self.nl_end, pos=(1, 0))
        sizer.Add(self.TTS_on, pos=(0, 1))
        sizer.Add(self.TTS_outside, pos=(1, 1))


class PreferencesTabs(wx.Notebook):

    """Preference tabs."""

    def __init__(self, parent, engine):
        wx.Notebook.__init__(self, parent)

        general_tab = GeneralTab(self, engine)
        display_tab = DisplayTab(self, engine)
        accessibility_tab = AccessibilityTab(self, engine)
        self.AddPage(general_tab, t("ui.dialog.general"))
        self.AddPage(display_tab, t("ui.dialog.display"))
        self.AddPage(accessibility_tab, t("ui.dialog.accessibility"))
        self.general = general_tab
        self.display = display_tab
        self.accessibility = accessibility_tab

class PreferencesDialog(wx.Dialog):

    """Preferences dialog."""

    def __init__(self, engine):
        super(PreferencesDialog, self).__init__(None, title="Preferences")
        self.engine = engine

        self.InitUI()
        self.Maximize()

    def InitUI(self):
        sizer = wx.GridBagSizer(15, 15)
        self.SetSizer(sizer)

        # Add the tabs
        self.tabs = PreferencesTabs(self, self.engine)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)

        # Append to the sizer
        sizer.Add(self.tabs, pos=(1, 0), span=( 5, 5))
        sizer.Add(buttons, pos=(8, 0), span=(1, 2))

        # Event binding
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

        # Displaying
        self.tabs.general.SetFocus()

    def OnOK(self, e):
        """Save the preferences."""
        settings = self.engine.settings
        general = self.tabs.general
        display = self.tabs.display
        accessibility = self.tabs.accessibility
        new_language = general.get_selected_language()
        encoding = display.get_selected_encoding()
        old_language = settings["options.general.language"]
        settings["options.general.language"] = new_language
        settings["options.general.encoding"] = encoding
        tab_end = accessibility.tab_end.GetValue()
        nl_end = accessibility.nl_end.GetValue()
        settings["options.accessibility.tab_end"] = tab_end
        settings["options.accessibility.nl_end"] = nl_end
        settings["options.TTS.on"] = accessibility.TTS_on.GetValue()
        settings["options.TTS.outside"] = accessibility.TTS_outside.GetValue()
        settings["options"].write()
        if old_language != new_language:
            wx.MessageBox(t("ui.dialog.message.update_language"),
                    t("ui.dialog.restart"), wx.OK | wx.ICON_INFORMATION)
        self.Destroy()

    def OnCancel(self, e):
        """Simply exit the dialog."""
        self.Destroy()
