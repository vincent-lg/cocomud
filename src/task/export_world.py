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

"""Asynchronous task to export a world to a zip archive."""

import os
from zipfile import ZipFile

from ytranslate import t

from task.base import BaseTask
from ui.dialogs.task import TaskDialog

class ExportWorld(BaseTask):

    """Task used to export a world to a ZIP file."""

    def __init__(self, world, filename, configuration, to_copy=None):
        """Initialize the task.

        Parameters:
            world (World): the world to be exported.
            filename (str): the file name to be written as a ZIP archive.
            configuration (str): the content of the 'config.set' file to be created.
            to_copy (list): optional list of file names to copy in the archive.

        """
        BaseTask.__init__(self)
        self.world = world
        self.filename = filename
        self.configuration = configuration
        self.to_copy = to_copy or []
        self.title = t("task.export_world.title")
        self.message = t("task.export_world.message")
        self.confirmation = t("task.export_world.confirmation")
        self.dialog = TaskDialog(self, self.title.format(progress=0))
        self.dialog.message = self.message
        self.dialog.confirmation = self.confirmation

    def execute(self):
        """Export the world, creating the ZIP archive."""
        nb_files = len(self.to_copy) + 2
        current_progress = 0
        step_progress = int(round(100 / nb_files))
        copied = []
        path = self.world.path
        message = self.message + " {}%"
        with ZipFile(self.filename, "w") as file:
            # Copy the 'options.conf' file
            file.write(os.path.join(path, "options.conf"), "world/options.conf")
            copied.append("options.conf")
            current_progress += step_progress
            self.update(text=message.format(current_progress),
                    progress=current_progress)

            # Copy the / config.set/  file using the new configuration
            file.writestr("world/config.set", self.configuration)
            copied.append("config.set")
            current_progress += step_progress
            self.update(text=message.format(current_progress),
                    progress=current_progress)

            # Copy all the other files to be copied
            for filename in self.to_copy:
                filename = filename.replace("\\", "/")
                if filename in copied:
                    continue

                file.write(os.path.join(path, filename), "world/" + filename)
                current_progress += step_progress
                self.update(text=message.format(current_progress),
                        progress=current_progress)

        self.update(text=message.format(100), progress=100)
