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

"""File conaining the logging facility for CocoMUD.

Import this class from anywhere in the program to manipulate loggers.  Top-level functions are used and return configured loggers, although furthering the configuration is still possible.

Example:

>>> from log import logger
>>> sharp_logger = logger("sharp")
>>> # Notice that, if the logger already exists, it will be returned

"""

from datetime import datetime
import logging
import os

class CustomFormatter(logging.Formatter):

    """Special formatter to add hour and minute."""

    def format(self, record):
        """Add special placeholders for shorter messages."""
        now = datetime.now()
        record.hour = now.hour
        record.minute = now.minute
        return logging.Formatter.format(self, record)


loggers = {}

def logger(name):
    """Return an existing or new logger.

    The name should be a string like 'sharp' to create the child
    logger 'cocomud.sharp'.  The log file 'logs/{name}.log' will be
    created.

    If the name is specified as an empty string, a main logger is
    created.  It will have the name 'cocomud' and will write both
    in the 'logs/main.log' file and to the console (with an INFO
    level).

    """
    if not name:
        filename = os.path.join("logs", "main.log")
        name = "cocomud"
        address = "main"
    else:
        address = name
        filename = os.path.join("logs", name + ".log")
        name = "cocomud." + name

    if address in loggers:
        return loggers[address]

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    formatter = CustomFormatter(
            "%(hour)02d:%(minute)02d [%(levelname)s] %(message)s")

    # If it's the main logger, create a stream handler
    if name == "cocomud":
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    # Create the file handler
    handler = logging.FileHandler(filename, encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    loggers[address] = logger
    return logger

MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

def get_date_formats():
    """Return the date formats in a dictionary."""
    now = datetime.now()
    formats = {
        "year": now.year,
        "month": MONTHS[now.month - 1],
        "weekday": WEEKDAYS[now.weekday()],
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
    }
    return formats

def begin():
    """Log the beginning of the session to every logger."""
    formats = get_date_formats()

    # Message to be sent
    message = "CocoMUD started on {weekday}, {month} {day}, {year}"
    message += " at {hour:>02}:{minute:>02}:{second:>02}"
    message = message.format(**formats)
    for logger in loggers.values():
        logger.propagate = False
        logger.info(message)
        logger.propagate = True

def end():
    """Log the end of the session to every logger."""
    formats = get_date_formats()

    # Message to be sent
    message = "CocoMUD stopped on {weekday}, {month} {day}, {year}"
    message += " at {hour:>02}:{minute:>02}:{second:>02}"
    message = message.format(**formats)
    for logger in loggers.values():
        logger.propagate = False
        logger.info(message)
        logger.propagate = True

# Prepare the different loggers
if not os.path.exists("logs"):
    os.mkdir("logs")

logger("")  # Main logger
logger("client")  # Client logger
logger("sharp")  # SharpEngine logger
logger("ui")  # User Interface logger
