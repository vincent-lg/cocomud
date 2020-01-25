# Copyright (c) 2016-2020, LE GOFF Vincent
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

"""Module containing functions to handle the keyboard."""

## Constants

# Modifiers
MOD_ALT = 1
MOD_CTRL = 2
MOD_SHIFT = 4
MOD_WINDOWS = 8

# Key codes
CODE_TO_KEY = {
    8: "Backspace",
    13: "Enter",
    27: "Escape",
    32: "Space",
    310: "Pause",
    324: "PavNum0",
    325: "PavNum1",
    326: "PavNum2",
    327: "PavNum3",
    328: "PavNum4",
    329: "PavNum5",
    330: "PavNum6",
    331: "PavNum7",
    332: "PavNum8",
    333: "PavNum9",
    340: "F1",
    341: "F2",
    342: "F3",
    343: "F4",
    344: "F5",
    345: "F6",
    346: "F7",
    347: "F8",
    348: "F9",
    349: "F10",
    350: "F11",
    351: "F12",
    364: "NumLock",
    387: "PavNum*",
    388: "PavNum+",
    390: "PavNum-",
    391: "PavNum.",
    392: "PavNum/",
}

KEY_TO_CODE = {}
for code, key in CODE_TO_KEY.items():
    KEY_TO_CODE[key.lower()] = code

# Add a few keys in the KEY_TO_CODE dictionary, as names may differ
KEY_TO_CODE["esc"] = 27
KEY_TO_CODE["back"] = 8
KEY_TO_CODE["return"] = 13
KEY_TO_CODE["pavnumlock"] = 364
KEY_TO_CODE["pavlock"] = 364

## Functions
def key_name(code, modifiers):
    """Return the key name, if found."""
    if code in CODE_TO_KEY:
        name = CODE_TO_KEY[code]
    elif 0 < code < 256:
        name = chr(code).upper()
    else:
        return ""

    ctrl = modifiers & MOD_CTRL != 0
    alt = modifiers & MOD_ALT != 0
    shift = modifiers & MOD_SHIFT != 0
    windows = modifiers & MOD_WINDOWS != 0
    if shift:
        name = "Shift + " + name
    if alt:
        name = "Alt + " + name
    if ctrl:
        name = "Ctrl + " + name
    if windows:
        name = "Windows + " + name

    return name

def key_code(name):
    """Return the key code as a tuple.

    The returned key code is a tuple containing two integers:
        code: The key code as present in the constants
        modifiers: A binary value of active modifiers

    For example:
        (8, 0) means Backspace (no modifiers)
        (340, 1) means Alt + F1
        (13, 6) means Ctrl + Shift + Enter
        (107, 2) means Ctrl + K

    """
    # Remove spaces
    name = name.replace(" ", "").lower()

    # Scan for modifiers
    modifiers = ("shift", "ctrl", "control", "alt")
    active_modifiers = 0
    while name:
        found = False
        for modifier in modifiers:
            if name.startswith(modifier):
                name = name[len(modifier):]
                if modifier == "alt":
                    active_modifiers = active_modifiers | MOD_ALT
                elif modifier in ("ctrl", "control"):
                    active_modifiers = active_modifiers | MOD_CTRL
                elif modifier == "shift":
                    active_modifiers = active_modifiers | MOD_SHIFT

                found = True
                break

        if name and name[0] in "+-":
            name = name[1:]

        if not found:
            break

    if len(name) == 1:
        code = ord(name.upper())
    elif name not in KEY_TO_CODE:
        raise ValueError("The key {} cannot be found".format(
                repr(name)))
    else:
        code = KEY_TO_CODE[name]

    return (code, active_modifiers)
