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

from StringIO import StringIO
import os
from urllib2 import urlopen

from ytranslate import t

from log import task as logger
from task.base import BaseTask
from ui.dialogs.task import TaskDialog

class Download(BaseTask):

    """Task used to download a file."""

    def __init__(self, filename, url, background=False):
        """Initialize the task.

        Parameters:
            filename: the name of file to be created (or None).
            url: the url of the file to be downloaded.
            background (default False): should the task run in the background?

        If the filename is None, then download in memory.  The file
        attribute will contain a StringIO pointing to this object.

        """
        BaseTask.__init__(self)
        self.filename = filename
        self.file = StringIO() if filename is None else None
        self.url = url
        if background:
            self.dialog = None
        else:
            self.dialog = TaskDialog(self, t("task.download.title",
                    url=url, progress=0))
            self.dialog.confirmation = t("task.download.confirmation")

    def cancel(self):
        """If the task is cancelled, delete the file."""
        BaseTask.cancel(self)
        if self.file:
            self.file = None

        if self.filename and os.path.exists(self.filename):
            os.remove(self.filename)

    def execute(self):
        """Download the file at the URL."""
        logger.debug("Task {}: preparing to download {}".format(self,
                self.url))
        response = urlopen(self.url)
        meta = response.info()
        encoding = response.headers['content-type'].split('charset=')[-1]
        size = int(meta.getheaders("Content-Length")[0])
        logger.debug("Task {}: size={}, encoding={}".format(self,
                size, encoding))
        chunk_size = 4096
        if self.filename is None:
            file = self.file
        else:
            file = open(self.filename, "wb")

        try:
            keep = True
            progress = 0.0
            percent = 0
            self.update(title=t("task.download.title",
                        url=self.url, progress=0),
                        text=t("task.download.downloading",
                        url=self.url, percent=0))

            while keep:
                old_percent = percent
                progress += chunk_size
                percent = round((progress / size) * 100, 1)
                if int(percent) != int(old_percent):
                    self.update(title=t("task.download.title",
                            url=self.url, percent=int(percent)),
                            text=t("task.download.downloading",
                            url=self.url, percent=int(percent)),
                            progress=int(percent))

                chunk = response.read(chunk_size)
                if not chunk:
                    keep = False

                file.write(chunk)
            file.seek(0)
        finally:
            if self.filename is not None:
                file.close()
