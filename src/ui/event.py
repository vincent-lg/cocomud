"""This file contains the specifial events for the CocoMUD client."""

import wx

# Constants
myEVT_FOCUS = wx.NewEventType()
EVT_FOCUS = wx.PyEventBinder(myEVT_FOCUS, 1)

class FocusEvent(wx.PyCommandEvent):

    """Change focus from the input field to the password field."""

    def __init__(self, etype, eid, value=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        """Return the event's value."""
        return self._value
