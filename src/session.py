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

"""This file contains the Session class."""

from datetime import datetime
import os
from pathlib import Path

from bus import Events, Hooks
from log import client as log
from scripts import Scripts
from sharp.engine import SharpScript

class Session:

    """A class representing a session.

    A session is an object linking together a world, a client and the
    GUI tab behind it.  Several sessions can be connected to the same
    world, using various clients.

    """

    current_sid = 0

    def __init__(self, client, world):
        self.sid = self.current_sid
        type(self).current_sid += 1
        self.client = client
        self.world = world
        self.character = None
        self.engine = None
        self.should_log = False
        self._sharp_engine = None
        self.hooks = Hooks()
        self.events = Events(handler=self.run_world_events)
        self.msdp_reports = []
        self.gmcp_supports = []
        self.scripts = Scripts(self)

    def __repr__(self):
        return f"<Session {self.sid} to the world {self.world and self.world.name or 'unknown'}>"

    @property
    def sharp_engine(self):
        if self._sharp_engine:
            return self._sharp_engine

        log.debug(f"Creating a SharpEngine for session {self.sid} (world: {'yes' if self.world else 'no'}, client: {'yes' if self.client else 'no'}, character: {'yes' if self.character else 'no'}, engine: {'yes' if self.engine else 'no'})")
        self._sharp_engine = SharpScript(self.engine, self.client, self.world)
        return self._sharp_engine

    def run_world_events(self, key, **kwargs):
        """Run the world's `#event` handlers for this key.

        Return whether one ran.  The arguments of the event become
        variables of the actions.

        """
        world = self.world
        if world is None:
            return False

        with world.lock:
            events = [event for event in world.events if event.matches(key)]

        for event in events:
            event.sharp_engine = self.sharp_engine
            event.execute(**kwargs)

        return bool(events)

    def bind_client(self, client):
        """Bind a newly-built client to the session.

        The client's Telnet options fire the session's hooks.  Each
        connection builds a new client, so the MSDP reports and GMCP
        supports asked by the scripts are given to it again.

        """
        self.client = client
        hooks = self.hooks
        msdp = client.protocols["msdp"]
        gmcp = client.protocols["gmcp"]
        msdp.add_listener(lambda name, value:
                hooks.fire("msdp", name, value, key=name))
        gmcp.add_listener(lambda package, data:
                hooks.fire("gmcp", package, data, key=package))
        msdp.report(*self.msdp_reports)
        gmcp.support(*self.gmcp_supports)

    def log_message(self, message):
        """Log a message, if set."""

        if self.should_log and message:
            directory = Path() / self.world.path
            if self.character:
                directory /= self.character.location
            directory /= "logs"
            if not directory.exists():
                directory.mkdir(parents=True)

            today = datetime.today()
            filename = today.strftime("%Y-%m-%d.log")
            filepath = directory / filename
            encoding = self.engine.settings["options.general.encoding"]
            message = message.rstrip("\n\r")
            message = os.linesep.join(message.splitlines()) + os.linesep
            message = message.encode(encoding, errors="replace")

            with filepath.open("ab") as file:
                file.write(message)

    def log_command(self, command):
        """Log a command."""
        should = self.engine.settings["options.logging.commands"]
        if should:
            msg = "\n".join([f"> {l}" for l in command.splitlines()])
            self.log_message(msg)
