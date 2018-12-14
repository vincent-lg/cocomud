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

import re, string

import wx
import wx.lib.colourdb

from .base import BaseExtension

## Constants
# Regular expressions to capture ANSI codes
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
        super().__init__(panel)
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

        # Position mark and style
        self.last_mark = None
        self.start_mark = None

    def OnClearOutput(self):
        """The output has been cleared."""

        # We must clear all data for styles
        self.modifiers = []
        self.start_mark = None
        self.last_mark = None

    def OnMessage(self, message):
        """Interpret the ANSI codes."""

        # Variables
        point = self.panel.editing_pos
        ansi_stage = 1
        ansi_buffer = ""
        clean_buffer = ""
        char_index = 0

        def select_colors(code):
            """
            Transforms ANSI sequences in a format specifier
            """

            match = RE_CODE.match(code)

            # ANSI style sequences have tree parts
            p1, p2, p3 = match.groups()
            brightness, foreground, background = (None, None, None)

            if p1:
                p1 = int(p1.strip())

                if p1 in (0, 1, 4, 7):
                    brightness = p1
                elif p1 in range(30, 38):
                    foreground = p1
                elif p1 in range(40, 48):
                    background = p1

            if p2:
                p2 = int(p2.strip())

                if p2 in range(30, 40):
                    foreground = p2
                elif p2 in range(40, 50):
                    background = p2

            if p3:
                p3 = int(p3.strip())

                if p3 in range(40, 50):
                    background = p3

            if brightness == 1:
                brightness = BRIGHT
            elif brightness == 4:
                brightness = UNDERLINE
            else:
                brightness = NORMAL


            # Now the colors
            colorlist = None

            if brightness == BRIGHT:
                colorlist = self.bright_colors
            elif brightness == UNDERLINE:
                colorlist = self.dark_colors
            else:
                colorlist = self.normal_colors

            if foreground:
                foreground = colorlist[foreground+10]
            else:
                foreground = self.default_foreground

            if background:
                background = colorlist[background]
            else:

                if brightness == BRIGHT:
                    background = wx.BLACK
                elif brightness == UNDERLINE:
                    background = wx.YELLOW
                else:
                    background = self.default_background

            return (foreground, background)

        # We must iterate over the entire message string
        while char_index < len(message):

            # First stage: look for a 0x1B character and switch to second stage
            if ansi_stage == 1:
                if message[char_index] == "\x1B":
                    ansi_stage = 2
                else:

                    # We must discard \r characters because it causes problems at formatting time
                    if message[char_index] != "\r":
                        clean_buffer += message[char_index]

            # Second stage: look for a validation character (an '[')
            elif ansi_stage == 2:
                if message[char_index] == "[":
                    ansi_stage = 3
                    ansi_buffer = ""
                else:
                    ansi_stage = 1

                    # Just add the two last characters
                    clean_buffer += message[char_index-1:char_index]

            # Last stage: process ANSI command with arguments
            elif ansi_stage == 3:
                if message[char_index] in string.digits+";":
                    ansi_buffer += message[char_index]

                # Now we have all arguments and the command (too generic detection for now...)
                else:
                    ansi_stage = 1
                    self.modifiers.append((point+len(clean_buffer), select_colors(ansi_buffer)))

                    ansi_buffer = ""

            char_index += 1


        return clean_buffer

    def PostMessage(self, message):
        """Applies ANSI style to text"""

        for point, style in self.modifiers:
            if not self.last_mark:
                self.last_mark = style
                self.start_mark = point
                continue

            # Unpack foreground and background from style tuple
            foreground, background = self.last_mark

            self.panel.output.SetStyle(self.start_mark, point, wx.TextAttr(
                    foreground, background))

            self.start_mark = point
            self.last_mark = style

        self.modifiers = []
