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

"""Module containing the LockInput extension."""

import wx

from accesspanel.extensions.base import BaseExtension

class LockInput(BaseExtension):

    """Implement a lock-in-input mode.

    In this mode, the user cannot use tab or shift-tab to leave the
    input field.  The cases in which the lock is applied can be changed
    through the extension's settings.

    Behavior of the extension can be altered through attributes:
        empty: the lock will be active unless the input is empty

    >>> import wx
    >>> from accesspanel import AccessPanel
    >>> class MyAccessPanel(AccessPanel):
    ...     def __init__(self, parent):
    ...         AccessPanel.__init__(self, parent, lock_input=True)
    ...         # Configure the lock
    ...         lock = self.extensions["lock_input"]
    ...         lock.empty = True

    Default values:
        input: False

    If you with to modify these default values, see the example above.

    """

    def __init__(self, panel):
        BaseExtension.__init__(self, panel)

        # Features that can be set in the AccessPanel
        self.empty = False

    def OnKeyDown(self, modifiers, key):
        """Prevent changing focus with tab/shift-tab."""
        skip = True
        if modifiers in (wx.MOD_NONE, wx.MOD_SHIFT) and key == wx.WXK_TAB:
            if not self.empty:
                skip = False
            elif self.panel.input:
                skip = False

        return skip
