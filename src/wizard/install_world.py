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

"""Wizard to import a world in the client."""

from collections import OrderedDict
import json

from ui.wizard.install_world import InstallWorld as UI

class InstallWorld:

    """A wizard to install a world in the client."""

    def __init__(self, engine, name, files, ui=True):
        """Constructor of the wizard.

        Arguments:
            engine: the game engine.
            name: name of the world to be imported.
            files: a dictionary containing ["name": "content"}.
            ui: should a UI be created for this wizard?

        """
        self.engine = engine
        self.name = name
        self.files = files
        if ui:
            self.dialog = UI(self.engine, self)
        else:
            self.dialog = None

    def start(self):
        """Display the UI, or assume default values."""
        if self.dialog:
            data = self.dialog.data
            self.dialog.ShowModal()
        else:
            data = {}
            install = self.files.get("world/install.json")
            if install:
                values = json.loads(install, encoding="utf-8",
                        object_pairs_hook=OrderedDict)

                for key, value in values.items():
                    default = value.get("default")
                    data[key] = default

        print "ret", data
        return data
