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

import re

import wx
import wx.lib.colourdb

from accesspanel.extensions.base import BaseExtension

## Constants
# Regular expressions to capture ANSI codes
RE_ANSI = re.compile(r'\x1b\[([^m]*)m', re.UNICODE)
RE_CODE = re.compile(r"^(?:(\d+)(?:\;(\d+)(?:\;(\d+))?)?)?$", re.UNICODE)

# Brightness
NORMAL = 1
BRIGHT = 2
UNDERLINE = 3

class ANSI(BaseExtension):

    """Manage the ANSI codes to have color in the text.

    The AccessPanel can support color codes. This extension allows
    to write ANSI color codes and put the text in correct formatting.

    Brief reminder:
        ANSI codes are placed in the text, between a '\x1b[' sequence
        and a final 'm'. In between are numbers separated with a
        semicolon.  The first number represents the level of
        brightness (0 for normal, 1 for bright, 4 for underline,
        7 for negative).  The second number represents the foreground
        color and should be between 30 and 37 (see the list below).
        The third number represents the background color and should be
        between 40 and 47 (the same list of color applies).

    List of colors:
        | Color      | Foreground | Background |
        | Black      | 30         | 40         |
        | Red        | 31         | 41         |
        | Green      | 32         | 42         |
        | Yellow     | 33         | 43         |
        | Blue       | 34         | 44         |
        | Magenta    | 35         | 45         |
        | Cyan       | 36         | 46         |
        | White      | 37         | 47         |

    Examples:
        "\x1b[0;31;47m" means red on white.
        "\x1b[1;33m" means bright yellow on default background.
        "\x1b[4;36m" means underline cyan on default background.
        "\x1b[0m" means back to default colors.

    """

    def __init__(self, panel):
        BaseExtension.__init__(self, panel)
        wx.lib.colourdb.updateColourDB()
        self.brightness = NORMAL
        self.foreground = wx.BLACK
        self.background = wx.WHITE
        self.default_foreground = wx.BLACK
        self.default_background = wx.WHITE
        self.modifiers = []

        # Color codes
        self.normal_colors = {
            40: wx.NamedColour("dark grey"),
            41: wx.RED,
            42: wx.GREEN,
            43: wx.YELLOW,
            44: wx.BLUE,
            45: wx.NamedColour("magenta"),
            46: wx.CYAN,
            47: wx.WHITE,
        }

        self.bright_colors = {
            40: wx.NamedColour("grey"),
            41: wx.NamedColour("deep pink"),
            42: wx.NamedColour("light green"),
            43: wx.NamedColour("light yellow"),
            44: wx.NamedColour("light blue"),
            45: wx.NamedColour("light magenta"),
            46: wx.NamedColour("light cyan"),
            47: wx.WHITE,
        }

        self.dark_colors = {
            40: wx.BLACK,
            41: wx.NamedColour("dark red"),
            42: wx.NamedColour("dark green"),
            43: wx.NamedColour("orange"),
            44: wx.NamedColour("dark blue"),
            45: wx.NamedColour("dark magenta"),
            46: wx.NamedColour("dark cyan"),
            47: wx.WHITE,
        }

    def OnClearOutput(self):
        """The output has been cleared."""
        self.modifiers = []

    def OnMessage(self, message):
        """Interpret the ANSI codes."""
        point = self.panel.editing_pos
        pos = []

        # Browse through the ANSI codes
        for match in reversed(list(RE_ANSI.finditer(message))):
            code = match.group(1)

            # Extract the brightness, foreground and background
            codes = RE_CODE.search(code)
            if codes:
                brightness, foreground, background = codes.groups()

                # All 3 variables can be None
                if brightness == 1:
                    brightness = BRIGHT
                elif brightness == 4:
                    brightness = UNDERLINE
                else:
                    brightness = NORMAL

                # Extract the foreground color
                if foreground:
                    foreground = int(foreground)
                    if brightness == NORMAL:
                        foreground = self.normal_colors.get(foreground + 10)
                    elif brightness == BRIGHT:
                        foreground = self.bright_colors.get(foreground + 10)
                    elif brightness == UNDERLINE:
                        foreground = self.dark_colors.get(foreground + 10)

                # Extract the background color
                if background:
                    background = int(background)
                    if brightness == NORMAL:
                        background = self.normal_colors.get(background)
                    elif brightness == BRIGHT:
                        background = self.bright_colors.get(background)
                    elif brightness == UNDERLINE:
                        background = self.dark_colors.get(background)

                if foreground is None:
                    foreground = self.default_foreground

                if brightness:
                    self.brightness = brightness

                if background is None:
                    if self.brightness == BRIGHT:
                        background = wx.BLACK
                    elif self.brightness == UNDERLINE:
                        background = wx.YELLOW
                    else:
                        background = self.default_background

                start = match.start()
                end = match.end()
                pos.append((start, end, foreground, background))

        begin_tag = True
        updated_pos = 0
        last_mod = None
        for start, end, foreground, background in reversed(pos):
            if begin_tag:
                begin_tag = False
            else:
                eol = message.count("\r", 0, start - 1)
                begin_tag = True
                real_start, m_foreground, m_background = last_mod
                real_start += point
                real_start -= eol
                real_end = start - updated_pos + point
                real_end -= eol
                self.modifiers.append((real_start, real_end, m_foreground,
                        m_background))

                # If it's not the default color, mark an open tag
                if foreground != self.default_foreground or \
                        background != self.default_background:
                    begin_tag = False

            last_mod = (start - updated_pos, foreground, background)
            updated_pos += end - start

        # Remove the ANSI codes from the message
        for start, end, foreground, background in pos:
            message = message[:start] + message[end:]

        return message

    def PostMessage(self, message):
        for start, end, foreground, background in self.modifiers:
            range = self.panel.output.GetRange(start, end)
            self.panel.output.SetStyle(start, end, wx.TextAttr(
                    foreground, background))
