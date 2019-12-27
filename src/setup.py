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

import distutils
import opcode
import os
import shutil

from cx_Freeze import setup, Executable

client = Executable(
    script="cocomud.py",
    base="Win32GUI",
)

updater = Executable(
    script="updater.py",
    base="Win32GUI",
)

dbg_updater = Executable(
    script="dbg_updater.py",
)

distutils_path = os.path.join(os.path.dirname(opcode.__file__), 'distutils')
includefiles = [
    (distutils_path, 'lib/distutils'),
    # The 'pubsub' package has to be copied from the virtual environment
    (os.path.join(os.environ["VIRTUAL_ENV"], 'lib', 'site-packages', 'pubsub', 'utils'), 'lib/pubsub/utils'),
    "translations",
    "worlds",
    "../doc",
    "../settings",

    # Requests
    "cacert.pem",
]

if os.path.exists("build/CocoMUD"):
    shutil.rmtree("build/CocoMUD")

setup(
    name = "CocoMUD client",
    version = "0.2",
    description = "The CocoMUD client.",
    options = {'build_exe': {
            "include_files": includefiles,
            "excludes": ["_gtkagg", "_tkagg", "bsddb", "distutils", "curses",
                    "pywin.debugger", "pywin.debugger.dbgcon",
                    "pywin.dialogs", "tcl", "Tkconstants", "Tkinter"],
            "packages": ["accesspanel", "redminelib.resources", "_cffi_backend", "idna.idnadata", "pubsub.pub"],
            "namespace_packages": ["zope.interface"],
    }},
    executables = [client, updater, dbg_updater]
)

shutil.move("build/exe.win32-3.6", "build/CocoMUD")
if os.name == "nt":
    for library in os.listdir("../lib/windows"):
        shutil.copyfile("../lib/windows/" + library, "build/CocoMUD/" + library)
