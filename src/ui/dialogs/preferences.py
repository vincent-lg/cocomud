﻿# Copyright (c) 2016-2020, LE GOFF Vincent
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
        l_languages = wx.StaticText(self,
                label=t("ui.dialog.preferences.general"))
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
        l_encodings = wx.StaticText(self, label=t("ui.dialog.preferences.encodings"))
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


class InputTab(wx.Panel):

    """Input tab."""

    def __init__(self, parent, engine):
        super(InputTab, self).__init__(parent)
        self.engine = engine

        self.InitUI()
        self.Fit()

    def InitUI(self):
        settings = self.engine.settings
        sizer = wx.GridBagSizer(15, 15)
        self.SetSizer(sizer)

        # Command stacking
        l_stacking = wx.StaticText(self,
                label=t("ui.dialog.preferences.command_stacking"))
        t_stacking = wx.TextCtrl(self,
                value=settings["options.input.command_stacking"])
        self.command_stacking = t_stacking

        # Help on command stacking
        h_stacking = wx.Button(self,
                label=t("ui.button.what.command_stacking"))

        # Auto-send
        self.auto_send_paste = wx.CheckBox(self,
                label=t("ui.dialog.preferences.auto_send_paste"))
        self.auto_send_paste.SetValue(settings["options.input.auto_send_paste"])

        # Append to the sizer
        sizer.Add(l_stacking, pos=(0, 0))
        sizer.Add(t_stacking, pos=(1, 0))
        sizer.Add(h_stacking, pos=(0, 1))
        sizer.Add(self.auto_send_paste, pos=(2, 0))

        # Event binding
        h_stacking.Bind(wx.EVT_BUTTON, self.OnHelpStacking)

    def OnHelpStacking(self, e):
        """Open the help for command stacking."""
        self.engine.open_help("CommandStacking")


class LoggingTab(wx.Panel):

    """Logging tab."""

    def __init__(self, parent, engine):
        super().__init__(parent)
        self.engine = engine

        self.InitUI()
        self.Fit()

    def InitUI(self):
        settings = self.engine.settings
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Logging preferendces
        s_logging = wx.BoxSizer(wx.HORIZONTAL)
        self.automatic = wx.CheckBox(self,
                label=t("ui.dialog.preferences.logger.automatic"))
        self.automatic.SetValue(settings["options.logging.automatic"])
        self.commands = wx.CheckBox(self,
                label=t("ui.dialog.preferences.logger.commands"))
        self.commands.SetValue(settings["options.logging.commands"])

        # Append to the sizer
        s_logging.Add(self.automatic)
        s_logging.Add(self.commands)

        # Add to the main sizer
        sizer.Add(s_logging)


class AccessibilityTab(wx.Panel):

    """Accessibility tab."""

    def __init__(self, parent, engine):
        super(AccessibilityTab, self).__init__(parent)
        self.engine = engine

        self.InitUI()
        self.Fit()

    def InitUI(self):
        settings = self.engine.settings
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # TTS preferendces
        s_TTS = wx.BoxSizer(wx.HORIZONTAL)
        self.TTS_on = wx.CheckBox(self,
                label=t("ui.dialog.preferences.TTS.on"))
        self.TTS_on.SetValue(settings["options.TTS.on"])
        self.TTS_outside = wx.CheckBox(self,
                label=t("ui.dialog.preferences.TTS.outside"))
        self.TTS_outside.SetValue(settings["options.TTS.outside"])
        self.TTS_interrupt = wx.CheckBox(self,
                label=t("ui.dialog.preferences.TTS.interrupt"))
        self.TTS_interrupt.SetValue(settings["options.TTS.interrupt"])

        # Append to the sizer
        s_TTS.Add(self.TTS_on)
        s_TTS.Add(self.TTS_outside)
        s_TTS.Add(self.TTS_interrupt)

        # RichTextControl
        s_other = wx.BoxSizer(wx.HORIZONTAL)
        self.richtext = wx.CheckBox(self,
                label=t("ui.dialog.preferences.richtext"))
        self.richtext.SetValue(settings["options.output.richtext"])
        s_other.Add(self.richtext)

        # Screen reader support (srs)
        s_srs = wx.BoxSizer(wx.HORIZONTAL)
        self.srs_on = wx.CheckBox(self,
                label=t("ui.dialog.preferences.screenreader"))
        self.srs_on.SetValue(settings["options.general.screenreader"])
        s_other.Add(self.srs_on)

        # Add to the main sizer
        sizer.Add(s_TTS)
        sizer.Add(s_other)


class PreferencesTabs(wx.Notebook):

    """Preference tabs."""

    def __init__(self, parent, engine):
        wx.Notebook.__init__(self, parent)

        general_tab = GeneralTab(self, engine)
        display_tab = DisplayTab(self, engine)
        input_tab = InputTab(self, engine)
        logging_tab = LoggingTab(self, engine)
        accessibility_tab = AccessibilityTab(self, engine)
        self.AddPage(general_tab, t("ui.dialog.preferences.general"))
        self.AddPage(display_tab, t("ui.dialog.preferences.display"))
        self.AddPage(input_tab, t("ui.dialog.preferences.input"))
        self.AddPage(logging_tab, t("ui.dialog.preferences.logging"))
        self.AddPage(accessibility_tab, t("ui.dialog.preferences.accessibility"))
        self.general = general_tab
        self.display = display_tab
        self.input = input_tab
        self.logging = logging_tab
        self.accessibility = accessibility_tab

class PreferencesDialog(wx.Dialog):

    """Preferences dialog."""

    def __init__(self, window, engine):
        super(PreferencesDialog, self).__init__(None, title="Preferences")
        self.window = window
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
        input = self.tabs.input
        logging = self.tabs.logging
        accessibility = self.tabs.accessibility
        new_language = general.get_selected_language()
        encoding = display.get_selected_encoding()
        command_stacking = input.command_stacking.GetValue()
        old_language = settings.get_language()
        interrupt = accessibility.TTS_interrupt.GetValue()
        old_richtext = settings["options.output.richtext"]
        auto_send_paste = input.auto_send_paste.GetValue()
        richtext = accessibility.richtext.GetValue()
        srs = accessibility.srs_on.GetValue()
        settings["options.general.language"] = new_language
        settings["options.general.encoding"] = encoding
        settings["options.general.screenreader"] = srs
        settings["options.input.command_stacking"] = command_stacking
        settings["options.input.auto_send_paste"] = auto_send_paste
        settings["options.TTS.on"] = accessibility.TTS_on.GetValue()
        settings["options.TTS.outside"] = accessibility.TTS_outside.GetValue()
        settings["options.TTS.interrupt"] = interrupt
        settings["options.logging.automatic"] = logging.automatic.GetValue()
        settings["options.logging.commands"] = logging.commands.GetValue()
        settings["options.output.richtext"] = richtext
        settings["options"].write()
        self.engine.TTS_on = accessibility.TTS_on.GetValue()
        self.engine.TTS_outside = accessibility.TTS_outside.GetValue()

        # Repercute screen reader support
        for tab in self.window.tabs.GetChildren():
            tab.screenreader_support = srs

        self.window.gameMenu.Check(
            self.window.chk_log.GetId(), logging.automatic.GetValue()
        )
        if old_language != new_language:
            wx.MessageBox(t("ui.dialog.preferences.update_language"),
                    t("ui.button.restart"), wx.OK | wx.ICON_INFORMATION)
        elif old_richtext != richtext:
            wx.MessageBox(t("ui.dialog.preferences.update_richtext"),
                    t("ui.button.restart"), wx.OK | wx.ICON_INFORMATION)

        self.EndModal(wx.ID_OK)

    def OnCancel(self, e):
        """Simply exit the dialog."""
        self.EndModal(wx.ID_OK)

