"""This module defines the default configuration."""

import os
import os.path
from textwrap import dedent

from configobj import ConfigObj
from validate import Validator

class Configuration:

    """Class describing CocoMUD's configuration.

    Each configuration file is loaded here. Each file is loaded and validated with ConfigObj.  If everything goes smoothly, the ConfigObj objects can be found in _getitem__-ing these values, specifying the directory structure.

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

    def __init__(self, root_dir):
        self.root_dir = root_dir
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

    def load_file(self, filename, spec):
        """Load the specified file using ConfigObj."""
        fullpath = self.root_dir + os.sep + filename

        # Create the directory structure if necessary
        directories = os.path.dirname(fullpath).split("/")
        base = directories[0]
        if not os.path.exists(base):
            os.mkdir(base)

        for directory in directories[1:]:
            base += os.path + directory
            if not os.path.exists(base):
                os.mkdir(base)

        filename = os.path.basename(fullpath) + ".conf"

        # Create the ConfigObj
        config = ConfigObj(fullpath + ".conf", configspec=spec.split("\n"))

        # Validates the configuration
        validator = Validator()
        result = config.validate(validator)

        # Saves the ConfigObj
        values = self.values
        for path in os.path.dirname(fullpath).split("/")[1:]:
            if path not in values:
                values[path] = {}
            values = values[path]

        values[os.path.basename(fullpath)] = config


class Settings(Configuration):

    """Special configuration in the 'settings' directory."""

    def __init__(self):
        Configuration.__init__(self, "settings")

    def load(self):
        """Load all the files."""
        self.load_options()

    def load_options(self):
        """Load the file containing the options."""
        spec = dedent("""
            # Text-to-speech configuration
            [TTS]
                on = boolean(default=True)
                outside = boolean(default=True)
        """.strip("\n"))
        self.load_file("options", spec)
