"""Package containing the sharp script."""

from sharp.function import Function
from sharp.functions.macro import Macro
from sharp.functions.play import Play
from sharp.functions.say import Say
from sharp.functions.trigger import Trigger
from sharp.functions.tts import TTS

FUNCTIONS = {
    "macro": Macro,
    "play": Play,
    "say": Say,
    "trigger": Trigger,
    "tts": TTS,
}
