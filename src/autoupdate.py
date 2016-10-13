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

"""This file contains the AutoUpdate class."""

import json
import os
import shutil
import sys
from threading import Thread
from urllib2 import urlopen
from zipfile import ZipFile, BadZipfile

class AutoUpdate(Thread):

    """Class to perform an automatic update.

    An object of this class is used to perform an automatic update.
    This can be triggered by a standalone program (required when the
    update actually performs), but some methods of its object can
    be used to check for updates and do not leave the application.

    """

    def __init__(self, current_version, object=None):
        Thread.__init__(self)
        if isinstance(current_version, basestring):
            if not current_version.isdigit():
                raise ValueError("the current version {} isn't an int".format(
                        repr(current_version)))
            else:
                current_version = int(current_version)

        self.current_version = current_version
        self.location = None
        self.path_archive = None
        self.object = object

    def run(self):
        """Run the thread."""
        if self.check():
            self.download()
            self.update()

    def check(self):
        """Check for updates."""
        if self.object:
            self.object.UpdateText("Checking for updates.")
            self.object.UpdateGauge(0)

        url = "https://cocomud.plan.io/projects/cocomud-client.json"
        response = urlopen(url)
        try:
            info = json.loads(response.read())
        except ValueError:
            raise UpdateDecodeError

        # The latest builds are in a custom field
        customs = info.get("project", {}).get("custom_fields")
        recent_build = None
        for field in customs:
            if field['name'] == "build":
                recent_build = field['value']

        # If a recent build has been found, try to read it
        if recent_build:
            try:
                recent_build = json.loads(recent_build)
            except ValueError:
                raise UpdateDecodeError
        else:
            raise UnavailableUpdateError

        # If everything went according to plan, recent_build is a dictionary
        # with build: {locations}
        new_build = list(recent_build.keys())[0]
        if new_build.isdigit():
            new_build = int(new_build)
        else:
            raise InvalidSyntaxUpdateError

        # If the recent build is greated than the current one
        if new_build > self.current_version:
            platform = ""
            if sys.platform == "win32":
                platform = "windows"

            location = recent_build[str(new_build)].get(platform)
            if location:
                self.location = location
                return True
            else:
                raise UknownPlatformUpdateError


    def download(self, stdout=False):
        """Download the build."""
        if self.object:
            self.object.UpdateText("Downloading...")
            self.object.UpdateGauge(0)

        # Creates a new folder for updates
        if os.path.exists("updating"):
            shutil.rmtree("updating")

        os.mkdir("updating")
        if stdout:
            print "Downloading the build at", self.location

        # Get the build
        response = urlopen(self.location)
        meta = response.info()
        size = int(meta.getheaders("Content-Length")[0])
        chunk_size = 4096
        path_archive = os.path.join("updating", "build.zip")
        with open(path_archive, "wb") as file:
            keep = True
            progress = 0.0
            percent = 0
            if stdout:
                sys.stdout.write("  Downloading...   0.0%")
                sys.stdout.flush()

            while keep:
                old_percent = percent
                progress += chunk_size
                percent = round((progress / size) * 100, 1)
                if self.object and int(percent) != int(old_percent):
                    self.object.UpdateGauge(int(percent))
                elif old_percent != percent and stdout:
                    sys.stdout.write("\r  Downloading... {:>5}%".format(
                            percent))
                    sys.stdout.flush()

                chunk = response.read(chunk_size)
                if not chunk:
                    keep = False

                file.write(chunk)

            if stdout:
                print "\r  Downloading... 100%"

        self.path_archive = path_archive

    def update(self, stdout=False):
        """Update the archive.

        This method must be called after downloading the new archive.
        Since it cannot perform all updates by itself (it would delete
        the updater and a couple of libraries), it needs to pass a batch
        file at the end that will delete itself.

        """
        if self.path_archive is None:
            raise ValueError("the updated archive hasn't been downloaded")

        if self.object:
            self.object.UpdateText("Extracting files...")
            self.object.UpdateGauge(0)

        # Analyze the zip file
        try:
            with ZipFile(self.path_archive, "r") as archive:
                infos = archive.infolist()
                extract = []
                total = 0
                for info in infos:
                    name = info.filename
                    names = name.split("/")
                    if len(names) > 1 and names[1] in ("settings", "worlds"):
                        continue

                    total += info.file_size
                    extract.append(info)

                # Extract these files
                if stdout:
                    print "Extracting {}o".format(total)

                extracted = 0.0
                if stdout:
                    sys.stdout.write("  Extracting files...   0%")
                    sys.stdout.flush()

                percent = 0.0
                for info in extract:
                    old_percent = percent
                    percent = round(extracted / total * 100, 1)
                    if self.object and int(percent) != int(old_percent):
                        self.object.UpdateGauge(int(percent))
                    elif old_percent != percent and stdout:
                        sys.stdout.write("\r  Extracting files..." \
                                "   {:>5}%".format(percent))
                        sys.stdout.flush()

                    archive.extract(info.filename, "updating")
                    extracted += info.file_size

                if stdout:
                    print "\r  Extracting files... 100%"
        except BadZipfile:
            raise InvalidSyntaxUpdateError

        # Delete the archive
        os.remove(self.path_archive)

        # Move the content of the archive
        batch = "timeout 1 /NOBREAK"
        for name in os.listdir(os.path.join("updating", "CocoMUD")):
            path = os.path.join("updating", "CocoMUD", name)
            if os.path.isfile(name):
                batch += "\ndel /F /Q " + name
                batch += "\ncopy /V " + path + " " + name
            elif os.path.isdir(name):
                batch += "\nrmdir /Q /S " + name
                batch += "\nmd " + name
                batch += "\nxcopy /S " + path + " " + name


        # Add instructions to delete the clean update
        batch += "\nrmdir /S /Q updating"
        batch += "\nexit /B"

        # Write the batch file
        with open("updating.bat", "w") as file:
            file.write(batch)
        with open("bgupdating.bat", "w") as file:
            cmd = "start /B \"\" \"cmd /C updating.bat\" >> update.log 2>&1"
            cmd += "\nexit"
            file.write(cmd)

        if self.object:
            self.object.AskDestroy()
        os.startfile("bgupdating.bat")
        sys.exit(0)


# Exceptions
class UpdateError(RuntimeError):

    """An error occured dduring the update."""

    pass


class UpdateDecodeError(UpdateError):

    """The update couldn't be decoded."""

    pass


class UnavailableUpdateError(UpdateError):

    """The update cannot be reached."""

    pass


class InvalidSyntaxUpdateError(UpdateError):

    """Something went wrong in the syntax of the build."""

    pass


class UknownPlatformUpdateError(UpdateError):

    """No platform could be found for this build."""

    pass
