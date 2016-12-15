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

"""Asynchronous task to import worlds from the website."""

from collections import namedtuple
from redmine import Redmine

from task.base import BaseTask
from ui.dialogs.task import TaskDialog

World = namedtuple("World", ["name", "author", "updated_on", "description"])

class ImportWorlds(BaseTask):

    """Task used to import worlds from the CocoMUD website.

    This method doesn't download the worlds.  It simply downloads
    their name, author, date and description.

    """

    def __init__(self, background=False, title="Loading",
            message="Downloading the world list..",
            confirmation="Do you want to cancel loading?"):
        """Initialize the task.

        Parameters:

            background (default False): should the task run in bthe background?
            title: title of the dialog to display.
            message: message of the dialog to display.
            confirmation: message when pressing on cancel in the dialog.

        """
        BaseTask.__init__(self)
        self.worlds = []
        self.title = title
        self.message = message
        self.confirmation = confirmation
        if background:
            self.dialog = None
        else:
            self.dialog = TaskDialog(self, title.format(progress=0))
            self.dialog.message = message
            self.dialog.confirmation = confirmation

    def execute(self):
        """Download the file at the URL."""
        message = self.message + " {}%"
        redmine = Redmine("https://cocomud.plan.io")
        self.update(text=message.format(5), progress=5)
        pages = redmine.wiki_page.filter(project_id="worlds")
        self.update(text=message.format(10), progress=10)
        size = len(pages) - 1
        self.update(text=message.format(15), progress=15)
        progress_per_task = 85.0 / size / 3
        progress = 15
        for page in pages:
            if page.title == "Wiki":
                continue

            title = page.title
            progress += progress_per_task
            self.update(text=message.format(int(progress)),
                    progress=int(progress))
            author = page.author.name
            progress += progress_per_task
            self.update(text=message.format(int(progress)),
                    progress=int(progress))
            updated_on = page.updated_on
            description = page.text
            progress += progress_per_task
            self.update(text=message.format(int(progress)),
                    progress=int(progress))
            world = World(title, author, updated_on, description)
            self.worlds.append(world)

        self.update(text=message.format(100), progress=100)
