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

"""This file contains the debug updater.

It's a console updater that plans on updating CocoMUD client.

"""

import argparse
import os

from autoupdate import AutoUpdate
from version import BUILD

parser = argparse.ArgumentParser()
parser.add_argument("-z", "--zip", action="store_true",
        help="Update from a build.zip file instead of downloading the update")
args = parser.parse_args()

autoupdate = AutoUpdate(BUILD, None)
if args.zip:
    archive = "updating/build.zip"
    if not os.path.exists(archive):
        print(f"The archived build {archive!r} couldn't be found.")
    else:
        autoupdate.path_archive = archive
        autoupdate.update(stdout=True)
else:
    print("Checking for updates...")
    build = autoupdate.check()
    if build is not None:
        print("A new update is available: {}.\n".format(build))
        autoupdate.download(stdout=True)
        autoupdate.update(stdout=True)
    else:
        print("No update is available, but download anyway.")
        autoupdate.download(stdout=True)
        autoupdate.update(stdout=True)

    os.system("pause")
