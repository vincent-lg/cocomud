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

"""Module containing the base class for extensions."""

class BaseExtension:

    """Base class for extensions.

    Extensions can had features to the AccessPanel.  They can override
    features of the AccessPanel, like its handling of keyboard
    shortcuts, in a way defined by the AccessPanel itself.  Extensions
    aren't mixin classes, the AccessPanel doesn't inherit from them,
    it implements them in a given list (see the AccessPanel class).

    """

    def __init__(self, panel):
        self.panel = panel

    def OnInput(self, text):
        """Override this method to change the way OnInput behaves.

        This method should return the text, that can be altered.  The
        extensions' 'OnInput' method will be called before the
        AccessPanel's implementation, which allows modifications of
        the text.

        """
        return text

    def OnMessage(self, text):
        """Alter the message sent to the AccessPanel.

        The given message is sent to the AccessPanel after the
        extensions have modified it.  This method should also return
        the modified text.

        """
        return text

    def PostMessage(self, message):
        """The message has been updated successfully>"""
        pass

    def OnClearOutput(self):
        """The output has been cleared."""
        pass

    def OnKeyDown(self, modifiers, key):
        """Add keyboard handling for this extension.

        This method should return whether this event should be skipped
        or not.  If it is skipped, then the key press will stop at
        this extension.  If not, it is passed along other extensions
        and, ultimately, to the AccessPanel itself if no other extension
        requires it to be skipped.

        """
        return True
