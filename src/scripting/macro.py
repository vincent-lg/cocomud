"""Class containing the Macro class."""

from scripting.key import key_name

class Macro:

    """A macro object.

    In a MUD client terminology, a macro is a link between a shortcut
    key and an action that is sent to the MUD.  For example, the F1
    shortcut could send 'north' to the MUD.

    """

    def __init__(self, key, modifiers, action):
        self.key = key
        self.modifiers = modifiers
        self.action = action

    def __repr__(self):
        return "<Macro {}: {}>".format(self.shortcut, self.action)

    @property
    def shortcut(self):
        """Return the key name."""
        return key_name(self.key, self.modifiers)

    def execute(self, engine, client):
        """Execute the macro."""
        client.write(self.action + "\r\n")
