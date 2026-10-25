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
    send(text)              send commands to the server, skipping
                            aliases and script commands.
    note(text)              display (and speak) text like received text.
    speak(text)             only speak text with the screen reader.
    channels                the channels: `channels.feed(name, text)`
                            adds a message to the session's history,
                            creating the channel if needed (hidden, not
                            saved in config.set).
    audio                   the audio library ('audio' package), whose
                            relative paths are relative to the world.
    msdp, gmcp              the Telnet options (`msdp.report(...)`,
                            `gmcp.send_message(...)`...).  Reports and
                            supports are kept across reconnections.
    settings                persistent settings of the world, a
                            dictionary saved in 'settings.json' and
                            shared by all sessions (`ScriptSettings`).
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

from collections.abc import MutableMapping
import json
import os
import traceback
from types import ModuleType

from twisted.internet import reactor

from log import logger
from screenreader import ScreenReader
from scripting.channel import Channel

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
        settings = world.script_settings
        error = settings.load()
        if error:
            errors.append((os.path.basename(settings.path), error))

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
        self.channels = ScriptChannels(self.session, world)
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
                "channels": self.channels,
                "audio": self.audio,
                "msdp": self.msdp,
                "gmcp": self.gmcp,
                "settings": self.world.script_settings,
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
            client.write(line, alias=False, commands=False)

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


class ScriptChannels:

    """The `channels` object of scripts.

    Channels created here are hidden by default and aren't saved in
    the world's config.set.  A channel the player created with
    #channel is used as it is.

    """

    def __init__(self, session, world):
        self.session = session
        self.world = world

    def add(self, name, visible=False):
        """Return the channel of this name, created if needed."""
        for channel in self.world.channels:
            if channel.name == name:
                return channel

        channel = Channel(self.world, name, visible=visible, saved=False)
        self.world.add_channel(channel)
        return channel

    def feed(self, name, text):
        """Add a message to a channel of the session, return it."""
        self.add(name)
        return self.session.history(name).feed(text)

    def history(self, name):
        """Return the session's history of a channel."""
        return self.session.history(name)


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


class ScriptSettings(MutableMapping):

    """Persistent settings of a world, shared by its scripts.

    It's a dictionary saved as JSON in 'worlds/<world>/settings.json'.
    Keys are strings and values must be JSON values (None, booleans,
    numbers, strings, lists and dictionaries of them): anything else
    raises TypeError when it's set.

    Each change schedules a save, half a second later, so that many
    changes in a row are written once.  Changing a list or dictionary
    stored as a value isn't noticed: set it again, or call `save`.

    A file that can't be read is renamed to 'settings.json.bad' rather
    than being overwritten, and the settings start empty.

    """

    delay = 0.5

    def __init__(self, path):
        self.path = path
        self.data = {}
        self.loaded = False
        self.pending = None
        self.reactor = reactor
        self.logger = logger("scripts")

    def __repr__(self):
        return "<ScriptSettings {!r}>".format(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError("setting keys must be strings, not {!r}".format(
                    key))

        try:
            json.dumps(value)
        except (TypeError, ValueError) as err:
            raise TypeError("the setting {!r} can't be saved: {}".format(
                    key, err)) from None

        self.data[key] = value
        self.schedule()

    def __delitem__(self, key):
        del self.data[key]
        self.schedule()

    def load(self):
        """Load the settings, if not loaded yet.

        Return None, or the traceback of the error if the file
        couldn't be read.

        """
        if self.loaded:
            return None

        self.loaded = True
        if not os.path.exists(self.path):
            return None

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError("the settings aren't a JSON object")
        except (OSError, ValueError):
            self.logger.exception("Cannot read the settings {}".format(
                    self.path))
            error = traceback.format_exc()
            try:
                os.replace(self.path, self.path + ".bad")
            except OSError:
                self.logger.exception("Cannot rename {}".format(self.path))
            return error

        self.data = data
        return None

    def schedule(self):
        """Schedule a save, unless one is already scheduled."""
        if self.pending is None or not self.pending.active():
            self.pending = self.reactor.callLater(self.delay, self.save)

    def save(self):
        """Save the settings now, cancelling a scheduled save."""
        if self.pending is not None and self.pending.active():
            self.pending.cancel()
        self.pending = None

        directory = os.path.dirname(self.path)
        temporary = self.path + ".tmp"
        try:
            os.makedirs(directory, exist_ok=True)
            with open(temporary, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4, sort_keys=True,
                        ensure_ascii=False)
            os.replace(temporary, self.path)
        except OSError:
            self.logger.exception("Cannot save the settings {}".format(
                    self.path))

    def flush(self):
        """Save the settings if a save is scheduled."""
        if self.pending is not None and self.pending.active():
            self.save()
