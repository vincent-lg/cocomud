"""Module containing functions to handle the keyboard."""

## Constants

# Modifiers
MOD_ALT = 1
MOD_CTRL = 2
MOD_SHIFT = 4

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
    398: "PavNum-",
}

KEY_TO_CODE = {}
for code, key in CODE_TO_KEY.items():
    KEY_TO_CODE[key] = code

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
        name = chr(code)
    else:
        return ""

    ctrl = modifiers & MOD_CTRL != 0
    alt = modifiers & MOD_ALT != 0
    shift = modifiers & MOD_SHIFT != 0
    if shift:
        name = "Shift + " + name
    if alt:
        name = "Alt + " + name
    if ctrl:
        name = "Ctrl + " + name

    return name
