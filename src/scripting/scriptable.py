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

"""File containing the Scriptable abstract class."""

class Scriptable:

    """An abstract scriptable.

    All scriptable objects in CocoMUD should inherit this class at some
    level.  This class offers mechanisms for propagating modifications to
    linked objects.  This is necessary because of the abstraction of
    configuration level: every piece of scritpable in CocoMUD can be
    defined on the general level, a world level, a character level,
    or a category level.  Thus, scriptables are often connected together
    and, for every modification, they have to modify their peers.

    """

    content = ()

    def __init__(self):
        self.duplicates = []

    def add_duplicate(self, scriptable):
        """Add the scriptable as a duplicate of self, if it's not the case.

        This method also adds self as a duplicate of scriptable.

        """
        if scriptable not in self.duplicates:
            self.duplicates.append(scriptable)
        if self not in scriptable.duplicates:
            scriptable.duplicates.append(self)

    def propagate(self):
        """Propagate the modifications to duplicates."""
        data = {}
        for name in type(self).content:
            value = getattr(self, name)
            data[name] = value

        # Browse the list of duplicates
        for scriptable in self.duplicates:
            for name, value in data.items():
                setattr(scriptable, name, value)
