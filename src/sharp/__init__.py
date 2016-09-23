"""Package containing the sharp script."""

from sharp.function import Function
from sharp.functions.play import Play
from sharp.functions.say import Say

FUNCTIONS = {
    "play": Play,
    "say": Say,
}