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

"""Module containing the character dialog."""

import wx

from ytranslate import t

class CharacterDialog(wx.Dialog):

    """Character dialog to change the character's preferences."""

    def __init__(self, engine, session):
        super(CharacterDialog, self).__init__(None,
                title=t("common.character", 1))
        self.engine = engine
        self.session = session

        self.InitUI()
        self.Center()

    def InitUI(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        s_name = wx.BoxSizer(wx.HORIZONTAL)
        s_username = wx.BoxSizer(wx.HORIZONTAL)
        s_password = wx.BoxSizer(wx.HORIZONTAL)
        s_post_login = wx.BoxSizer(wx.HORIZONTAL)
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.SetSizer(sizer)
        character = self.session.character

        # Create the dialog
        l_name = wx.StaticText(self, label=t("common.name"))
        t_name = wx.TextCtrl(self, value=character and character.name or "")
        self.name = t_name
        s_name.Add(l_name)
        s_name.Add(t_name)
        sizer.Add(s_name)

        # Create the user field
        l_username = wx.StaticText(self,
                label=t("ui.message.character.username"))
        t_username = wx.TextCtrl(self, style=wx.TE_MULTILINE,
                value=character and character.username or "")
        self.username = t_username
        s_username.Add(l_username)
        s_username.Add(t_username)
        sizer.Add(s_username)

        # Create the password field
        l_password = wx.StaticText(self,
                label=t("ui.message.character.password"))
        t_password = wx.TextCtrl(self, style=wx.TE_PASSWORD,
                value=character and character.password or "")
        self.password = t_password
        s_password.Add(l_password)
        s_password.Add(t_password)
        sizer.Add(s_password)

        # Create the post-login field
        l_post = wx.StaticText(self,
                label=t("ui.message.character.post_login"))
        t_post = wx.TextCtrl(self, style=wx.TE_MULTILINE,
                value=character and character.other_commands or "")
        self.post_login = t_post
        s_post_login.Add(l_post)
        s_post_login.Add(t_post)
        sizer.Add(s_post_login)

        # Create the 'default character' checkbox
        self.default = wx.CheckBox(self,
                label=t("ui.message.character.default"))
        self.default.SetValue(character and character.default or True)

        # Buttons
        sizer.Add(buttons)
        t_name.SetFocus()
        sizer.Fit(self)

        # Event binding
        self.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)

    def OnOK(self, e):
        """Save the character."""
        world = self.session.world
        character = self.session.character
        name = self.name.GetValue()
        username = self.username.GetValue()
        password = self.password.GetValue()
        post_login = self.post_login.GetValue()
        default = self.default.GetValue()
        if not name:
            wx.MessageBox(t("ui.message.character.missing_name"),
                    t("ui.alert.missing"), wx.OK | wx.ICON_ERROR)
            self.name.SetFocus()
        else:
            if character is None:
                character = world.add_character(name.lower())

            character.name = name
            character.username = username
            character.password = password
            character.other_commands = post_login
            character.default = default
            character.save()
            self.session.character = character

            # If 'default' is set to True, put other character.default
            # to False (there can only be one default character)
            for other in world.characters.values():
                if other is character:
                    continue

                if default and other.default:
                    other.default = False
                    other.save()

            self.Destroy()

    def OnCancel(self, e):
        """Simply exit the dialog."""
        self.Destroy()
