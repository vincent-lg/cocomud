"""Package containing the sharp script."""

from sharp.function import Function
from sharp.functions.alias import Alias
from sharp.functions.channel import Channel
from sharp.functions.feed import Feed
from sharp.functions.macro import Macro
from sharp.functions.play import Play
from sharp.functions.randplay import RandPlay
from sharp.functions.repeat import Repeat
from sharp.functions.say import Say
from sharp.functions.send import Send
from sharp.functions.trigger import Trigger
from sharp.functions.tts import TTS

FUNCTIONS = {
    "alias": Alias,
    "channel": Channel,
    "feed": Feed,
    "macro": Macro,
    "play": Play,
    "randplay": RandPlay,
    "repeat": Repeat,
    "say": Say,
    "send": Send,
    "trigger": Trigger,
    "tts": TTS,
}
