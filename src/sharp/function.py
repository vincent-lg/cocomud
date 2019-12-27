# Copyright (c) 2016-2020, LE GOFF Vincent
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

"""Module containing the Function class."""

from ytranslate import t

class Function(object):

    """The function class, parent of all SharpScript functions."""

    description = ""

    def __init__(self, engine, client, sharp, world=None):
        self.engine = engine
        self.client = client
        self.sharp_engine = sharp
        self.world = world
        self.init()

    def init(self):
        """Another secondary constructor."""
        pass

    def run(self, *args, **kwargs):
        """Execute the function with arguments."""
        raise NotImplementedError

    def display(self, panel):
        """Display the function's argument."""
        pass

    def complete(self, dialog, *args, **kwargs):
        """Complete the action."""
        return ()

    def t(self, address, default):
        """Translates the given address, returning a string.

        If the translation isn't available in the catalog, return the
        default value (presumably in English).  The address to be
        given is relative to the function (the address
        'sharp.function_name.{address}' will be sought).

        """
        address = "sharp.{name}.{address}".format(name=self.name,
                address=address)
        try:
            translation = t(address)
        except ValueError:
            translation = default

        return translation
