"""Package containing the sharp script."""

from sharp.function import Function
from sharp.functions.alias import Alias
from sharp.functions.channel import Channel
from sharp.functions.checkvar import Checkvar
from sharp.functions.feed import Feed
from sharp.functions.idle import Idle
from sharp.functions.macro import Macro
from sharp.functions.pause import Pause
from sharp.functions.play import Play
from sharp.functions.randplay import RandPlay
from sharp.functions.repeat import Repeat
from sharp.functions.say import Say
from sharp.functions.send import Send
from sharp.functions.trigger import Trigger
from sharp.functions.tts import TTS
from sharp.functions.writevar import Writevar

FUNCTIONS = {
    "alias": Alias,
    "channel": Channel,
    "checkvar": Checkvar,
    "feed": Feed,
    "idle": Idle,
    "macro": Macro,
    "pause": Pause,
    "play": Play,
    "randplay": RandPlay,
    "repeat": Repeat,
    "say": Say,
    "send": Send,
    "trigger": Trigger,
    "tts": TTS,
    "writevar": Writevar,
}
