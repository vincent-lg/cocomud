"""Class containing the Macro class."""

class Macro:

    """A macro object.

    In a MUD client terminology, a macro is a link between a shortcut
    key and an action that is sent to the MUD.  For example, the F1
    shortcut could send 'north' to the MUD.

    """

    def __init__(self, key, action, shift=False, ctrl=False, alt=False):
        self.key = key
        self.action = action
        self.shift = shift
        self.ctrl = ctrl
        self.alt = alt

    def __repr__(self):
        return "<Macro {}: {}>".format(self.printable_key, self.action)

    @property
    def printable_key(self):
        """Return the