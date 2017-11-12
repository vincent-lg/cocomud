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
import os
import wx

from ytranslate import t

from log import wizard as logger
from sharp.functions.channel import Channel
from ui.wizard.install_world import PreInstallDialog
from ui.wizard.install_world import InstallWorld as UI
from world import World

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
        self.dialog = None
        self.ui = ui

    def start(self):
        """Display the UI, or assume default values.

        The process of installing a world when connected to a
        user interface is as follows:

        1. The world to install or merge into is sought out.
        2. A dialog to select merging options is displayed.
        3. The installation dialog is displayed.

        """
        logger.info("Starting the wizard 'install_world' for '{}'".format(
                self.name))

        # 1. Look for the world, if any
        best = self.engine.get_world(self.name)
        worlds = []
        worlds = [self.engine.create_world(self.name)]
        if best is not None:
            worlds.insert(0, best)

        # Add the other worlds
        others = []
        for other in self.engine.worlds.values():
            if other not in worlds:
                others.append(other)

        others.sort(key=lambda w: w.name)
        worlds += others

        # 2. Create the dialog to select merging options
        if self.ui:
            logger.debug("Opening the PreInstallDialog")
            dialog = PreInstallDialog(self.engine, self.name, worlds)
            results = dialog.results
            dialog.ShowModal()
            destination = results.get("world")
            merge = results.get("merge")
            name = results.get("name")
            logger.debug("Obtained the settings: {}".format(results))
            if destination is None or merge is None:
                return

            # If the world hasn't a location or name
            if not destination.name:
                destination.name = name
                destination.location = name.lower()

            self.engine.prepare_world(destination, merge)
            destination.load()
        else:
            destination = worlds[0]
            merge = merging[0]
            name = destination.name

        # 3. Show the installation dialog
        if self.ui and "world/install.json" in self.files:
            logger.debug("Opening the installation dialog")
            self.dialog = UI(self.engine, self)
            data = self.dialog.data
            self.dialog.ShowModal()
            logger.debug("Obtained data={}".format(data))
        else:
            data = {}
            install = self.files.get("world/install.json")
            if install:
                values = json.loads(install, encoding="utf-8",
                        object_pairs_hook=OrderedDict)

                for key, value in values.items():
                    default = value.get("default")
                    data[key] = default

        Channel.allow_creation = False
        self.engine.prepare_world(destination, merge)
        sharp = destination.sharp_engine

        # Copy the options
        options = self.files.get("world/options.conf")
        if options:
            infos = World.get_infos(options)
            hostname = infos.get("connection", {}).get("hostname")
            port = int(infos.get("connection", {}).get("port"))
            destination.name = infos.get("connection", {}).get("name")
            destination.hostname = hostname
            destination.port = port

        # Install the world
        if "world/install.py" in self.files:
            logger.debug("Executing the installation file")
            install = self.files["world/install.py"]
            install = install.decode("utf-8").replace("\r", "")
            globals = sharp.globals
            locals = sharp.locals
            locals.update(data)
            exec(install, globals, locals)

        # Execute the 'config.set' file as is
        config = self.files.get("world/config.set")
        if config:
            logger.debug("Executing the config.set script")
            config = config.decode("utf-8")
            destination.sharp_engine.execute(config, variables=False)

        # Replace the allow_creation for channels
        Channel.allow_creation = True

        # Ensures the world is properly named
        destination.name = name

        # Just saves the world
        destination.save()
        destination.load()

        # Copy all the other files
        to_skip = ("config.set", "install.py", "install.json", "options.conf")
        for path, content in self.files.items():
            if path.endswith("/"):
                # It's a folder, we skip it
                continue

            relpath = os.path.relpath(path, "world")
            if relpath in to_skip:
                # We skip all these files
                continue

            abspath = os.path.join(destination.path, relpath)
            dirname = os.path.dirname(abspath)

            # If the parent directory doesn't exist, create it
            if not os.path.exists(dirname):
                logger.debug("Create the directory {}".format(dirname))
                os.makedirs(dirname)

            # Create the file itself
            logger.debug("Copy the file {}".format(abspath))
            with open(abspath, "wb") as file:
                file.write(content)

        # End of the wizard
        self.engine.prepare_world(destination, "ignore")
        logger.info("The world {} has been installed successfully".format(
                destination.name))
        # Add the world if not present
        if name not in self.engine.worlds:
            self.engine.worlds[name] = destination

        if self.ui:
            wx.MessageBox(t("wizard.install_world.success", world=name),
                    t("ui.alert.success"), wx.OK | wx.ICON_INFORMATION)
