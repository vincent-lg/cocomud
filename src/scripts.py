# Copyright (c) 2016-2026, LE GOFF Vincent
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

"""World scripts, Python modules reacting to hooks and firing events.

World scripts are the '.py' files in the 'scripts' folder of a world
('worlds/<world>/scripts/*.py').  They're loaded by each session
connecting to the world, in alphabetical order, so two sessions on
the same world don't share their state.

Scripts don't import their API: these names are in their globals.

    hook(name, key=None)    decorator registering a hook callback.
                            `@hook("msdp", "X")` also asks the server
                            to report the MSDP variable X.
    command(name)           decorator adding a command typed by the
                            player ("sound volume"), tested before
                            the aliases and not sent to the server.
    events                  `events.fire(key, **kwargs)`, and
                            `@events.listen(key)` to listen to an event.
    send(text)              send commands to the server (not aliases).
    note(text)              display (and speak) text like received text.
    speak(text)             only speak text with the screen reader.
    audio                   the audio library ('audio' package), whose
                            relative paths are relative to the world.
    msdp, gmcp              the Telnet options (`msdp.report(...)`,
                            `gmcp.send_message(...)`...).  Reports and
                            supports are kept across reconnections.
    world, session          the world and the session.

Example ('worlds/erion/scripts/music.py'):

    @hook("msdp", "AREA_NAME")
    def area_changed(name, value):
        if not events.fire("area", name=value):
            audio.channel("music", category="music").play(
                    "sounds/music/{}.ogg".format(value), loop=True)

    @hook("disconnect")
    def stop(reason):
        audio.channel("music").stop()

"""

import os
import traceback
from types import ModuleType

from log import logger
from screenreader import ScreenReader

class Scripts:

    """The world scripts loaded by a session."""

    def __init__(self, session):
        self.session = session
        self.loaded = False
        self.modules = {}
        self.hooks = []
        self.listeners = []
        self.commands = {}
        self.logger = logger("scripts")

    def load(self, world):
        """Load the scripts of this world.

        Return the list of errors as (filename, traceback) tuples.  A
        failing script doesn't prevent the others from being loaded,
        but the hooks and listeners it registered before failing stay.

        """
        self.loaded = True
        directory = os.path.join(world.path, "scripts")
        if not os.path.isdir(directory):
            return []

        errors = []
        api = API(self, world)
        for filename in sorted(os.listdir(directory)):
            path = os.path.join(directory, filename)
            if not filename.endswith(".py") or not os.path.isfile(path):
                continue

            name = filename[:-3]
            module = ModuleType("scripts." + name)
            module.__file__ = path
            module.__dict__.update(api.namespace())
            self.logger.info("Loading the script {}".format(path))
            try:
                with open(path, "r", encoding="utf-8") as file:
                    code = compile(file.read(), path, "exec")
                exec(code, module.__dict__)
            except Exception:
                self.logger.exception("The script {} failed".format(path))
                errors.append((filename, traceback.format_exc()))

            self.modules[name] = module

        return errors

    def unload(self):
        """Remove the hooks and listeners registered by the scripts."""
        session = self.session
        for name, callback, key in self.hooks:
            session.hooks.unregister(name, callback, key=key)

        for key, callback in self.listeners:
            session.events.unlisten(key, callback)

        self.hooks.clear()
        self.listeners.clear()
        self.commands.clear()
        self.modules.clear()
        self.loaded = False

    def reload(self, world):
        """Unload, then load the scripts again."""
        self.unload()
        return self.load(world)

    def run_command(self, text):
        """Run the script command matching the typed text, if any.

        A command matches the text if the text is the command's words,
        or begins with them followed by a space (ignoring case).  The
        longest matching command is called with the rest of the text.
        Return whether a command matched: its text isn't sent to the
        server, even if the command failed.

        """
        words = text.split()
        for size in range(len(words), 0, -1):
            name = " ".join(words[:size]).lower()
            callback = self.commands.get(name)
            if callback is None:
                continue

            args = text.strip()
            for word in words[:size]:
                args = args[len(word):].lstrip()

            try:
                callback(args)
            except Exception:
                self.logger.exception("The command {!r} failed".format(
                        text))

            return True

        return False


class API:

    """The names given to scripts, bound to a session."""

    def __init__(self, scripts, world):
        self.scripts = scripts
        self.session = scripts.session
        self.world = world
        self.events = ScriptEvents(scripts)
        self.audio = ScriptAudio(world)
        self.msdp = MSDPProxy(self.session)
        self.gmcp = GMCPProxy(self.session)

    def namespace(self):
        """Return the globals of a script."""
        return {
                "hook": self.hook,
                "command": self.command,
                "events": self.events,
                "send": self.send,
                "note": self.note,
                "speak": self.speak,
                "audio": self.audio,
                "msdp": self.msdp,
                "gmcp": self.gmcp,
                "world": self.world,
                "session": self.session,
        }

    def hook(self, name, key=None):
        """Decorator registering a hook callback."""
        def decorator(callback):
            self.session.hooks.register(name, callback, key=key)
            self.scripts.hooks.append((name, callback, key))
            if name == "msdp" and key is not None:
                self.msdp.report(key)
            return callback

        return decorator

    def command(self, name):
        """Decorator adding a command typed by the player.

        The name is one or more words ("sound volume").  The callback
        receives the rest of the typed text as a string.  Commands are
        tested before the aliases, and their text isn't sent.

        """
        def decorator(callback):
            self.scripts.commands[" ".join(name.split()).lower()] = callback
            return callback

        return decorator

    def send(self, text):
        """Send one or more commands to the server, without aliases."""
        client = self.session.client
        if client is None:
            self.scripts.logger.warning("Cannot send {!r}: not "
                    "connected".format(text))
            return

        for line in text.splitlines():
            client.write(line, alias=False)

    def note(self, text):
        """Display text like received text, speaking it if needed."""
        client = self.session.client
        if client is None:
            self.scripts.logger.info("Note: {}".format(text))
            return

        client.handle_message(text)

    def speak(self, text, interrupt=False):
        """Speak text with the screen reader, without displaying it."""
        ScreenReader.talk(text, interrupt=interrupt)


class ScriptEvents:

    """The `events` object of scripts."""

    def __init__(self, scripts):
        self.scripts = scripts

    def fire(self, key, **kwargs):
        """Fire an event, return whether it has been handled."""
        return self.scripts.session.events.fire(key, **kwargs)

    def listen(self, key):
        """Decorator adding an event listener.

        The listener returns True to mark the event as handled, or
        None if it only observes it.

        """
        def decorator(callback):
            self.scripts.session.events.listen(key, callback)
            self.scripts.listeners.append((key, callback))
            return callback

        return decorator


class ScriptAudio:

    """The audio library, with paths relative to the world.

    Everything else is the audio library itself ('audio' package):
    `audio.category(...)`, `audio.stop(...)` and so on.

    """

    def __init__(self, world):
        self.world = world

    def __getattr__(self, name):
        return getattr(self.library, name)

    @property
    def library(self):
        from audio import audiolib
        return audiolib

    def path(self, path):
        """Return the absolute path, relative paths being in the world."""
        return os.path.abspath(os.path.join(self.world.path, path))

    def play(self, path, *args, **kwargs):
        """Play a sound, see `AudioLib.play`."""
        return self.library.play(self.path(path), *args, **kwargs)

    def channel(self, *args, **kwargs):
        """Return a channel, see `AudioLib.channel`."""
        return ScriptChannel(self,
                self.library.channel(*args, **kwargs))


class ScriptChannel:

    """A channel whose relative paths are relative to the world."""

    def __init__(self, audio, channel):
        self.audio = audio
        self.channel = channel

    def __getattr__(self, name):
        return getattr(self.channel, name)

    def __setattr__(self, name, value):
        if name in ("audio", "channel"):
            super().__setattr__(name, value)
        else:
            setattr(self.channel, name, value)

    def play(self, path, *args, **kwargs):
        """Play a sound in the channel, see `Channel.play`."""
        return self.channel.play(self.audio.path(path), *args, **kwargs)


class ProtocolProxy:

    """A Telnet option of the session's current client.

    Each connection builds a new client.  The MSDP reports and GMCP
    supports are kept by the session, which gives them to every new
    client.  Other calls go to the current client's option.

    """

    name = None

    def __init__(self, session):
        self.session = session

    def __getattr__(self, name):
        client = self.session.client
        if client is None:
            raise RuntimeError("cannot use {}.{}: not connected".format(
                    self.name, name))

        return getattr(client.protocols[self.name], name)


class MSDPProxy(ProtocolProxy):

    """The MSDP option, see `protocol.msdp.MSDP`."""

    name = "msdp"

    def report(self, *names):
        """Ask the server to report MSDP variables, now and later."""
        added = [n for n in names if n not in self.session.msdp_reports]
        self.session.msdp_reports.extend(added)
        if self.session.client is not None:
            self.session.client.protocols["msdp"].report(*added)

    def unreport(self, *names):
        """Stop the reports of MSDP variables."""
        for name in names:
            if name in self.session.msdp_reports:
                self.session.msdp_reports.remove(name)

        if self.session.client is not None:
            self.session.client.protocols["msdp"].unreport(*names)


class GMCPProxy(ProtocolProxy):

    """The GMCP option, see `protocol.gmcp.GMCP`."""

    name = "gmcp"

    def support(self, *modules):
        """Add supported GMCP packages, now and later."""
        added = [m for m in modules if m not in self.session.gmcp_supports]
        self.session.gmcp_supports.extend(added)
        if self.session.client is not None:
            self.session.client.protocols["gmcp"].support(*added)
