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

"""This file contains the World class."""

from enum import Enum
import shutil
import os
import re
from StringIO import StringIO
from textwrap import dedent
from threading import RLock

from configobj import ConfigObj, ParseError
from ytranslate import t

from character import Character
from log import sharp as logger
from notepad import Notepad
from screenreader import ScreenReader
from session import Session

class MergingMethod(Enum):

    """Enumeration to represent merging methods."""

    ignore = 1
    replace = 2


class World:

    """A class representing a World object.

    A world is a game (a server).  It conatins a hostname and a port
    and optionally characters.

    """

    def __init__(self, location):
        self.location = location
        self.name = ""
        self.hostname = ""
        self.port = 4000
        self.protocol = "telnet"
        self.characters = {}
        self.settings = None
        self.lock = RLock()

        # World's access to general data
        self.engine = None
        self.sharp_engine = None

        # World's configuration
        self.aliases = []
        self.channels = []
        self.macros = []
        self.triggers = []
        self.notepad = None
        self.merging = MergingMethod.ignore

        # Auto completion
        self.words = {}
        self.ac_choices = []

    def __repr__(self):
        return "<World {} (hostname={}, port={})>".format(
                self.name, self.hostname, self.port)

    @property
    def path(self):
        """Return the path to the world."""
        return os.path.join("worlds", self.location)

    def load(self):
        """Load the config.set script."""
        from game import Level
        level = self.engine.level
        self.engine.level = Level.world

        # Reset some of the world's configuration
        self.aliases = []
        self.channels = []
        self.macros = []
        self.triggers = []

        path = self.path
        path = os.path.join(path, "config.set")
        if os.path.exists(path):
            file = open(path, "r")
            content = file.read()
            file.close()

            # Convert the content to unicode
            to_save = False
            try:
                content = content.decode("utf-8")
            except UnicodeError:
                logger.warning("Cannot read the world's configuration in " \
                        "utf-8, try in latin-1 and force-save")
                content = content.decode("latin-1", errors="replace")
                to_save = True

            # Execute the script
            self.sharp_engine.execute(content, variables=False)

        # Put the engine level back
        self.engine.level = level

        if to_save:
            self.save()

    def load_characters(self):
        """Load the characters."""
        location = self.path
        for directory in os.listdir(location):
            if os.path.isdir(os.path.join(location, directory)) and \
                    os.path.exists(os.path.join(location,
                    directory, ".passphrase")):
                character = Character(self, directory)
                logger.info("Loading the character {} from the world " \
                        "{}".format(directory, self.name))
                character.load()
                self.characters[directory] = character

    def save(self):
        """Save the world in its configuration file."""
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        spec = dedent("""
            [connection]
                name = "unknown"
                hostname = "unknown.ext"
                port = 0
                protocol = "telnet"
        """).strip("\n")

        if self.settings is None:
            try:
                self.settings = ConfigObj(spec.split("\n"), encoding="latin-1")
            except ParseError:
                logger.warning("Error while parsing the config file, " \
                        "trying without encoding")
                self.settings = ConfigObj(spec.split("\n"))
                self.settings.encoding = "latin-1"
                self.settings.write()

        connection = self.settings["connection"]
        connection["name"] = self.name
        connection["hostname"] = self.hostname
        connection["port"] = self.port
        connection["protocol"] = self.protocol
        self.settings.filename = os.path.join(self.path, "options.conf")
        self.settings.write()
        self.save_config()

    def save_config(self):
        """Save the 'config.set' script file."""
        lines = []

        # Aliases
        for alias in self.aliases:
            lines.append(alias.sharp_script)

        # Channels
        for channel in self.channels:
            lines.append("#channel {{{}}}".format(channel.name))

        # Macros
        for macro in self.macros:
            lines.append(macro.sharp_script)

        # Triggers
        for trigger in self.triggers:
            lines.append(trigger.sharp_script)

        content = "\n".join(lines) + "\n"
        path = self.path
        path = os.path.join(path, "config.set")
        file = open(path, "w")
        content = content.encode("utf-8")
        file.write(content)
        file.close()

    def remove(self):
        """Remove the world."""
        shutil.rmtree(self.path)

    def add_character(self, location, name=None):
        """Add a new character in the world."""
        name = name or location
        character = Character(self, location)
        character.name = name
        character.save()
        self.characters[name] = character
        return character

    def add_alias(self, alias):
        """Add the alias to the world's configuration, handling conflicts.

        If another alias with the same name exists, either replace
        it or ignore the second one.

        """
        for existing in self.aliases:
            if existing.alias == alias.alias:
                # There's a conflict, look at the 'merging' setting
                if self.merging == MergingMethod.ignore:
                    return
                elif self.merging == MergingMethod.replace:
                    existing.action = alias.action
                    existing.level = alias.level
                    return

        # Otherwise, just add it at the end
        self.aliases.append(alias)

    def add_channel(self, channel):
        """Add a channel, handling conflicts."""
        for existing in self.channels:
            if existing.name == channel.name:
                return

        # Otherwise, just add it at the end
        self.channels.append(channel)

    def add_macro(self, macro):
        """Add the macro to the world's configuration, handling conflicts.

        If another macro with the same shortcut exists, either replace
        it or ignore the second one.

        """
        for existing in self.macros:
            if existing.shortcut == macro.shortcut:
                # There's a conflict, look at the 'merging' setting
                if self.merging == MergingMethod.ignore:
                    return
                elif self.merging == MergingMethod.replace:
                    existing.action = macro.action
                    existing.level = macro.level
                    return

        # Otherwise, just add it at the end
        self.macros.append(macro)

    def add_trigger(self, trigger):
        """Add the trigger to the world's configuration, handling conflicts.

        If another trigger with the same reaction exists, either replace
        it or ignore the second one.

        """
        for existing in self.triggers:
            if existing.reaction == trigger.reaction:
                # There's a conflict, look at the 'merging' setting
                if self.merging == MergingMethod.ignore:
                    return
                elif self.merging == MergingMethod.replace:
                    existing.action = trigger.action
                    existing.mute = trigger.mute
                    existing.level = trigger.level
                    return

        # Otherwise, just add it at the end
        self.triggers.append(trigger)

    def reset_autocompletion(self):
        """Erase the list of possible choices in for the auto completion."""
        self.ac_choices[:] = []

    def feed_words(self, text):
        """Add new words using the provided text.

        Each word in this text will be added to the list of words for
        a future auto-completion.

        """
        for word in re.findall(r"(\w+)", text, re.UNICODE):
            word = word.lower()
            count = self.words.get(word, 0)
            count += 1
            self.words[word] = count

    def find_word(self, word, TTS=False):
        """Find the most likely word for auto-completion."""
        matches = {}
        word = word.lower()
        for potential, count in self.words.items():
            if potential.startswith(word):
                if potential not in self.ac_choices:
                    matches[potential] = count

        # Sort through the most common
        for potential, count in sorted(matches.items(),
                key=lambda tup: tup[1], reverse=True):
            self.ac_choices.append(potential)
            if TTS:
                ScreenReader.talk(potential)
            return potential

        return None

    def create_session(self, client):
        """Create a session attached to this world."""
        session = Session(client, self)
        session.engine = self.engine
        session.sharp_engine = self.sharp_engine
        return session

    def open_notepad(self):
        """Open and return the notepad associated to this world."""
        if self.notepad:
            return self.notepad

        self.notepad = Notepad(self)
        empty_string = t("ui.message.notepad.world_empty", world=self.name)
        self.notepad.open(empty_string)
        return self.notepad

    @classmethod
    def get_infos(cls, configuration):
        """Get the information in the configuration and return a dict."""
        config = ConfigObj(StringIO(configuration), encoding="latin-1")
        data = {}

        for key, value in config.items():
            if key == "port":
                try:
                    value = int(value)
                except ValueError:
                    pass

            data[key] = value

        return data
