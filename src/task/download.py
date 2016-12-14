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

import os
from urllib2 import urlopen

from task.base import BaseTask
from ui.dialogs.task import TaskDialog

class Download(BaseTask):

    """Task used to download a file."""

    def __init__(self, filename, url, background=False,
            title="Downloading {url}",
            downloading="Downloading... {percent}%",
            confirmation="Do you want to cancel this download?"):
        """Initialize the task.

        Parameters:
            filename: the name of file to be created.
            url: the url of the file to be downloaded.
            background (default False): should the task run in the background?
            title: the title of the window to be displayed.
            downloading: the message to be displayed while downloading.
            confirmation: message displayed if the user clicks on cancel.

        """
        BaseTask.__init__(self)
        self.filename = filename
        self.url = url
        self.title = title
        self.downloading = downloading
        if background:
            self.window = None
        else:
            self.window = TaskDialog(self, title.format(url=url, progress=0))
            self.window.confirmation = confirmation

    def __repr__(self):
        return "<{} (url={})>".format(type(self), self.url)

    def cancel(self):
        """If the task is cancelled, delete the file."""
        BaseTask.cancel(self)
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def execute(self):
        """Download the file at the URL."""
        response = urlopen(self.url)
        meta = response.info()
        size = int(meta.getheaders("Content-Length")[0])
        chunk_size = 4096
        with open(self.filename, "wb") as file:
            keep = True
            progress = 0.0
            percent = 0
            if self.window:
                self.window.UpdateTitle(self.title.format(
                        url=self.url, progress=0))
                self.window.UpdateProgress(0)
                self.window.UpdateText(self.downloading.format(
                        url=self.url, percent=0))

            while keep:
                self.check_active()
                old_percent = percent
                progress += chunk_size
                percent = round((progress / size) * 100, 1)
                if self.window and int(percent) != int(old_percent):
                    self.window.UpdateTitle(self.title.format(
                            url=self.url, percent=int(percent)))
                    self.window.UpdateText(self.downloading.format(
                            url=self.url, percent=int(percent)))
                    self.window.UpdateProgress(int(percent))

                chunk = response.read(chunk_size)
                if not chunk:
                    keep = False

                file.write(chunk)
