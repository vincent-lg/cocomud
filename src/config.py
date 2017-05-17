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

"""This module defines the default configuration."""

import locale
import os
import os.path
from textwrap import dedent

from yaml import safe_dump, safe_load
from configobj import ConfigObj
from validate import Validator

from world import World

class Configuration(object):

    """Class describing CocoMUD's configuration.

    Each configuration file is loaded here.  A configuration file can
    be either YAML or respecting the ConfigObj syntax (that is,
    basically a .ini file).  If everything goes smoothly, the ConfigObj
    objects can be found in __getitem__-ing these values, specifying
    the directory structure.

    Example:

        >>> config = Configuration()
        >>> config.load()
        >>> # In the settings/global.conf file is the following line:
        >>> #     name = CocoMUD
        >>> # You can access this configuration through:
        >>> configuration["options"]["global"]["name"]
        >>> # Or, more readable
        >>> configuration["options.global.name"]

    """

    def __init__(self, root_dir, engine):
        self.root_dir = root_dir
        self.engine = engine
        self.values = {}

    def __getitem__(self, key):
        """Return the configured value at the specified key.

        The key is a string.  It can be an identifier without periods
        (.).  In which case, the top-level data at this key is returned
        or a KeyError exception is raised.
        The 'key' can also be a list of identifiers in a string separated
        by a period.  In this case, the data is looked for in the
        directory/file/ConfigObj hierarchy.  A KeyError exception
        is raised if the expected key cannot be found.

        Thus, the two following lines are identical:
            >>> configuration["settings"]["global"]["name"]
            >>> configuration["settings.global.name"]

        """
        if "." in key:
            keys = key.split(".")
            value = self.values
            for sub_key in keys:
                if sub_key not in value:
                    raise KeyError("the key {} cannot be found, cannot " \
                            "find {}".format(repr(key), repr(sub_key)))

                value = value[sub_key]

        else:
            value = self.values[key]

        return value

    def __setitem__(self, key, value):
        """Change the value of 'key'.

        'key' is a string, and can be specified in the two ways supported
        by '__getitem__'.

        """
        if "." in key:
            keys = key.split(".")
            last = keys[-1]
            del keys[-1]
            dictionary = self.values
            for sub_key in keys:
                if sub_key not in dictionary:
                    raise KeyError("the key {} cannot be found, cannot " \
                            "find {}".format(repr(key), repr(sub_key)))

                dictionary = dictionary[sub_key]

            dictionary[last] = value
        else:
            self.values[key] = value

    def load(self):
        """Load the configuration."""
        raise NotImplementedError

    def load_config_file(self, filename, spec, root_dir=None):
        """Load the specified file using ConfigObj."""
        root_dir = root_dir or self.root_dir
        fullpath = os.path.join(root_dir, filename)

        # Create the directory structure if necessary
        directories = os.path.dirname(fullpath).split("/")
        base = directories[0]
        if not os.path.exists(base):
            os.mkdir(base)

        for directory in directories[1:]:
            base += os.path.sep + directory
            if not os.path.exists(base):
                os.mkdir(base)

        # Create the ConfigObj
        config = ConfigObj(fullpath + ".conf", configspec=spec.split("\n"))

        # Validates the configuration
        validator = Validator()
        result = config.validate(validator)

        # Saves the ConfigObj
        values = self.values
        for path in os.path.dirname(filename).split("/")[1:]:
            if path not in values:
                values[path] = {}
            values = values[path]

        values[os.path.basename(fullpath)] = config

    def load_YAML_file(self, filename):
        """Load the YAML file."""
        fullpath = self.root_dir + os.sep + filename
        if os.path.exists(fullpath + ".yml"):
            file = open(fullpath + ".yml", "r")
            datas = safe_load(file.read())
        else:
            datas = {}

        values = self.values
        for path in os.path.dirname(fullpath).split("/")[1:]:
            if path not in values:
                values[path] = {}
            values = values[path]

        values[os.path.basename(fullpath)] = datas

    def write_YAML_file(self, filename, data):
        """Write the YAML associated with the data.

        Arguments:
            filename: the filename relative to the rootdir without extension
            data: the data as a dictionary.

        """
        fullpath = self.root_dir + os.sep + filename + ".yml"
        file = open(fullpath, "w")
        try:
            safe_dump(data, file, default_flow_style=False)
        finally:
            file.close()


class Settings(Configuration):

    """Special configuration in the 'settings' directory."""

    LANGUAGES = (
        ("en", "English"),
        ("fr", "French"),
    )

    def __init__(self, engine):
        Configuration.__init__(self, "settings", engine)

    def get_language(self):
        """Return the configured language.

        If the configuration hasn't been loaded, or the configured
        language isn't valid, return "en" (English).

        """
        default = "en"
        codes = [c[0] for c in type(self).LANGUAGES]
        try:
            lang = self["options.general.language"]
            assert lang in codes
        except (KeyError, AssertionError):
            return default

        return lang

    def load(self):
        """Load all the files."""
        self.load_options()

        # Load the world configuration
        for directory in os.listdir("worlds"):
            world = World(location=directory)
            settings = GameSettings(self.engine, world)
            settings.load()
            self.engine.worlds[world.name] = world
            world.load_characters()

    def load_options(self):
        """Load the file containing the options."""
        lang = locale.getdefaultlocale()[0].split("_")[0]
        spec = dedent("""
            [general]
                language = option('en', 'fr', default='{lang}')
                encoding = string(default="iso8859_15")
                screenreader = boolean(default=True)

            [input]
                command_stacking = string(default=";")

            [output]
                richtext = boolean(default=True)

            [TTS]
                on = boolean(default=True)
                outside = boolean(default=True)
                interrupt = boolean(default=True)
        """.format(lang=lang).strip("\n"))
        self.load_config_file("options", spec)

    def write_macros(self):
        """Write the YAML data file."""
        macros = {}
        for macro in self.engine.macros.values():
            macros[macro.shortcut] = macro.action

        self.write_YAML_file("macros", macros)

class GameSettings(Configuration):

    """Game settings (specific to a game/world)."""

    def __init__(self, engine, world):
        Configuration.__init__(self, "settings", engine)
        self.world = world

    def load(self):
        """Load all the files."""
        self.load_options()

    def load_options(self):
        """Load the file containing the options."""
        world = self.world
        spec = dedent("""
            [connection]
                name = string
                hostname = string
                port = integer
                protocol = string(default="telnet")
        """).strip("\n")
        self.load_config_file("options", spec, world.path)
        world.name = self["options.connection.name"]
        world.hostname = self["options.connection.hostname"]
        world.port = self["options.connection.port"]
        world.protocol = self["options.connection.protocol"]
        world.settings = self["options"]
