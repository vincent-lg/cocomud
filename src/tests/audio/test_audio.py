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

"""Tests of the audio library, with a fake BASS module."""

from unittest.mock import patch
import unittest

from twisted.internet.task import Clock

from audio import pybass
from audio.wrapper import AudioLib

VOL = pybass.BASS_ATTRIB_VOL
PAN = pybass.BASS_ATTRIB_PAN
VOLDSP = pybass.BASS_ATTRIB_VOLDSP
LOOP = pybass.BASS_SAMPLE_LOOP
AUTOFREE = pybass.BASS_STREAM_AUTOFREE

class Stream:

    """A fake BASS stream."""

    def __init__(self, filename, flags):
        self.filename = filename
        self.flags = flags
        self.state = pybass.BASS_ACTIVE_STOPPED
        self.attributes = {}
        self.slides = {}
        self.syncs = []


class FakeBass:

    """A fake pybass module, keeping streams in memory.

    Constants come from the real module.  Streams behave as if
    created with `BASS_STREAM_AUTOFREE`: they're freed when stopped
    or when they end.

    """

    def __init__(self):
        self.streams = {}
        self.missing = set()
        self.last_error = 0
        self.next_handle = 1

    def __getattr__(self, name):
        value = getattr(pybass, name)
        if callable(value):
            raise AttributeError(f"{name} isn't faked")
        return value

    def get_error_description(self, code):
        return pybass.get_error_description(code)

    def SYNCPROC(self, function):
        return function

    def BASS_ErrorGetCode(self):
        return self.last_error

    def BASS_StreamCreateFile(self, mem, filename, offset, length, flags):
        if filename.decode("utf-8") in self.missing:
            self.last_error = pybass.BASS_ERROR_FILEOPEN
            return 0

        handle = self.next_handle
        self.next_handle += 1
        self.streams[handle] = Stream(filename.decode("utf-8"), flags)
        return handle

    def BASS_ChannelIsActive(self, handle):
        stream = self.streams.get(handle)
        return stream.state if stream else pybass.BASS_ACTIVE_STOPPED

    def BASS_ChannelPlay(self, handle, restart):
        self.streams[handle].state = pybass.BASS_ACTIVE_PLAYING
        return True

    def BASS_ChannelPause(self, handle):
        self.streams[handle].state = pybass.BASS_ACTIVE_PAUSED
        return True

    def BASS_ChannelStop(self, handle):
        return self.streams.pop(handle, None) is not None

    def BASS_ChannelSetAttribute(self, handle, attribute, value):
        stream = self.streams.get(handle)
        if stream is None:
            return False

        stream.attributes[attribute] = value
        stream.slides.pop(attribute, None)
        return True

    def BASS_ChannelSlideAttribute(self, handle, attribute, value, time):
        stream = self.streams.get(handle)
        if stream is None:
            return False

        stream.slides[attribute] = (value, time)
        return True

    def BASS_ChannelFlags(self, handle, flags, mask):
        stream = self.streams[handle]
        stream.flags = (stream.flags & ~mask) | flags
        return stream.flags

    def BASS_ChannelSetSync(self, handle, type, param, proc, user):
        self.streams[handle].syncs.append(proc)
        return 1

    def end(self, handle):
        """Simulate a stream reaching its end."""
        stream = self.streams.pop(handle)
        for proc in stream.syncs:
            proc(1, handle, 0, None)


class TestAudio(unittest.TestCase):

    """Base class for audio tests."""

    def setUp(self):
        self.bass = FakeBass()
        patcher = patch("audio.sound.pybass", self.bass)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.clock = Clock()
        self.audio = AudioLib()
        self.audio.has_init = True
        self.audio.call_later = self.clock.callLater
        self.audio.call_from_thread = lambda function, *args: function(*args)

    def stream(self, sound):
        """Return the fake stream of a sound."""
        return self.bass.streams[sound.bass_handle]


class TestSound(TestAudio):

    """Test sounds played by the library."""

    def test_play(self):
        """Test that the volume, pan and flags are set on the stream."""
        sound = self.audio.play("hit.ogg", volume=80, pan=-40)
        self.assertTrue(sound.playing)
        stream = self.stream(sound)
        self.assertEqual(stream.filename, "hit.ogg")
        self.assertEqual(stream.flags, AUTOFREE)
        self.assertEqual(stream.attributes, {VOL: 0.8, PAN: -0.4, VOLDSP: 1})

    def test_missing_file(self):
        """Test that a missing file gives a stopped sound with an error."""
        self.bass.missing.add("nope.ogg")
        sound = self.audio.play("nope.ogg")
        self.assertTrue(sound.stopped)
        self.assertEqual(sound.error, "can't open the file")
        self.assertEqual(self.audio.sounds, [])

    def test_loop(self):
        """Test looping, set when playing and changed while playing."""
        sound = self.audio.play("rain.ogg", loop=True)
        self.assertEqual(self.stream(sound).flags, AUTOFREE | LOOP)
        sound.loop = False
        self.assertEqual(self.stream(sound).flags, AUTOFREE)

    def test_volume_and_pan(self):
        """Test changing the volume and pan of a playing sound."""
        sound = self.audio.play("hit.ogg")
        sound.volume = 30
        sound.pan = 100
        self.assertEqual(self.stream(sound).attributes[VOL], 0.3)
        self.assertEqual(self.stream(sound).attributes[PAN], 1)

    def test_pause_resume(self):
        """Test pausing and resuming a sound."""
        sound = self.audio.play("hit.ogg")
        self.assertTrue(sound.pause())
        self.assertTrue(sound.paused)
        self.assertTrue(sound.resume())
        self.assertTrue(sound.playing)

    def test_stop_paused(self):
        """Test that a paused sound can be stopped."""
        sound = self.audio.play("hit.ogg")
        sound.pause()
        self.assertTrue(sound.stop())
        self.assertTrue(sound.stopped)

    def test_delay(self):
        """Test that a delayed sound only starts after its delay."""
        sound = self.audio.play("hit.ogg", delay=0.25)
        self.assertTrue(sound.pending)
        self.assertEqual(self.bass.streams, {})
        self.clock.advance(0.25)
        self.assertTrue(sound.playing)

    def test_delay_stop(self):
        """Test that stopping a delayed sound cancels it."""
        sound = self.audio.play("hit.ogg", delay=0.25)
        self.assertTrue(sound.stop())
        self.clock.advance(1)
        self.assertTrue(sound.stopped)
        self.assertEqual(self.bass.streams, {})

    def test_fade_in(self):
        """Test that a fade-in starts silent and slides the volume."""
        sound = self.audio.play("song.ogg", volume=60, fade_in=2)
        stream = self.stream(sound)
        self.assertEqual(stream.attributes[VOL], 0)
        self.assertEqual(stream.slides[VOL], (0.6, 2000))

    def test_fade(self):
        """Test sliding the volume and the pan."""
        sound = self.audio.play("song.ogg")
        sound.fade(volume=20, pan=-50, duration=1.5)
        self.assertEqual(self.stream(sound).slides,
                {VOL: (0.2, 1500), PAN: (-0.5, 1500)})
        self.assertEqual(sound.volume, 20)

    def test_fade_out(self):
        """Test that a fade-out slides to silence, then stops."""
        sound = self.audio.play("song.ogg", volume=70)
        self.assertTrue(sound.fade_out(2))
        self.assertTrue(sound.fading_out)
        self.assertEqual(self.stream(sound).slides[VOL], (0, 2000))
        self.clock.advance(1.9)
        self.assertTrue(sound.playing)
        self.clock.advance(0.1)
        self.assertTrue(sound.stopped)
        self.assertFalse(sound.fading_out)
        self.assertEqual(sound.volume, 70)

    def test_fade_out_cancelled(self):
        """Test that setting the volume cancels a fade-out."""
        sound = self.audio.play("song.ogg")
        sound.fade_out(2)
        sound.volume = 50
        self.clock.advance(3)
        self.assertTrue(sound.playing)
        self.assertEqual(self.stream(sound).slides, {})

    def test_fade_out_paused(self):
        """Test that a paused sound is stopped right away."""
        sound = self.audio.play("song.ogg")
        sound.pause()
        sound.fade_out(2)
        self.assertTrue(sound.stopped)

    def test_on_end(self):
        """Test that on_end is called when the sound ends."""
        ended = []
        sound = self.audio.play("hit.ogg")
        sound.on_end = ended.append
        self.bass.end(sound.bass_handle)
        self.assertEqual(ended, [sound])
        self.assertTrue(sound.stopped)

    def test_sounds(self):
        """Test that the library tracks sounds until they stop."""
        first = self.audio.play("first.ogg")
        second = self.audio.play("second.ogg")
        self.assertCountEqual(self.audio.sounds, [first, second])
        first.stop()
        self.assertEqual(self.audio.sounds, [second])
        first.play()
        self.assertCountEqual(self.audio.sounds, [first, second])


class TestCategory(TestAudio):

    """Test categories and the master volume."""

    def test_get_or_create(self):
        """Test that categories are created once, and updated."""
        combat = self.audio.category("combat", volume=40, label="Combat")
        self.assertIs(self.audio.category("combat"), combat)
        self.assertEqual(self.audio.categories, {"combat": combat})
        self.assertEqual(combat.volume, 40)
        self.assertEqual(combat.label, "Combat")
        self.assertEqual(self.audio.category("music").label, "music")

    def test_play_creates(self):
        """Test that playing in an unknown category creates it."""
        sound = self.audio.play("hit.ogg", category="combat")
        self.assertIs(sound.category, self.audio.categories["combat"])

    def test_volume(self):
        """Test that the category volume applies to its sounds only."""
        self.audio.category("combat", volume=50)
        first = self.audio.play("hit.ogg", category="combat", volume=80)
        second = self.audio.play("parry.ogg", category="combat")
        other = self.audio.play("song.ogg", category="music")
        self.assertEqual(self.stream(first).attributes[VOLDSP], 0.5)
        self.audio.categories["combat"].volume = 20
        self.assertEqual(self.stream(first).attributes[VOLDSP], 0.2)
        self.assertEqual(self.stream(second).attributes[VOLDSP], 0.2)
        self.assertEqual(self.stream(other).attributes[VOLDSP], 1)
        self.assertEqual(self.stream(first).attributes[VOL], 0.8)

    def test_volume_during_fade(self):
        """Test that changing a category volume doesn't stop a fade."""
        sound = self.audio.play("song.ogg", category="music")
        sound.fade_out(2)
        self.audio.categories["music"].volume = 30
        self.assertEqual(self.stream(sound).slides[VOL], (0, 2000))
        self.clock.advance(2)
        self.assertTrue(sound.stopped)

    def test_muted(self):
        """Test muting and unmuting a category."""
        combat = self.audio.category("combat", volume=60)
        sound = self.audio.play("hit.ogg", category=combat)
        combat.muted = True
        self.assertEqual(self.stream(sound).attributes[VOLDSP], 0)
        self.assertTrue(sound.playing)
        later = self.audio.play("parry.ogg", category=combat)
        self.assertEqual(self.stream(later).attributes[VOLDSP], 0)
        combat.muted = False
        self.assertEqual(self.stream(sound).attributes[VOLDSP], 0.6)

    def test_master_volume(self):
        """Test that the master volume multiplies the category volume."""
        sound = self.audio.play("hit.ogg", category="combat")
        self.audio.categories["combat"].volume = 50
        self.audio.volume = 50
        self.assertEqual(self.stream(sound).attributes[VOLDSP], 0.25)

    def test_stop(self):
        """Test stopping a category, the others keep on playing."""
        hit = self.audio.play("hit.ogg", category="combat")
        song = self.audio.play("song.ogg", category="music")
        self.audio.stop(category="combat")
        self.assertTrue(hit.stopped)
        self.assertTrue(song.playing)
        self.audio.stop(category="unknown")
        self.assertTrue(song.playing)

    def test_stop_all_with_fade(self):
        """Test stopping all sounds with a fade-out."""
        hit = self.audio.play("hit.ogg", category="combat")
        song = self.audio.play("song.ogg")
        self.audio.stop(fade=1)
        self.assertTrue(hit.fading_out)
        self.assertTrue(song.fading_out)
        self.clock.advance(1)
        self.assertEqual(self.audio.sounds, [])


class TestChannel(TestAudio):

    """Test channels, playing one sound at a time."""

    def setUp(self):
        super().setUp()
        self.music = self.audio.channel("music", category="music", fade=2)

    def test_get_or_create(self):
        """Test that channels are created once."""
        self.assertIs(self.audio.channel("music"), self.music)
        self.assertEqual(self.audio.channels, {"music": self.music})
        self.assertEqual(self.music.fade, 2)

    def test_play(self):
        """Test that the channel's category is used."""
        sound = self.music.play("area25.ogg", loop=True)
        self.assertEqual(self.music.filename, "area25.ogg")
        self.assertIs(sound.category, self.audio.categories["music"])
        self.assertTrue(sound.loop)

    def test_same_file(self):
        """Test that playing the same file again does nothing."""
        sound = self.music.play("area25.ogg", loop=True)
        self.assertIs(self.music.play("./area25.ogg", loop=True), sound)
        self.assertEqual(len(self.bass.streams), 1)

    def test_restart(self):
        """Test forcing a file to restart."""
        sound = self.music.play("area25.ogg")
        other = self.music.play("area25.ogg", restart=True, fade=0)
        self.assertIsNot(other, sound)
        self.assertTrue(sound.stopped)

    def test_replace(self):
        """Test that a new file fades the old one out."""
        old = self.music.play("area25.ogg")
        new = self.music.play("battle.ogg", fade_in=1)
        self.assertTrue(old.fading_out)
        self.assertTrue(new.playing)
        self.assertIs(self.music.sound, new)
        self.clock.advance(2)
        self.assertTrue(old.stopped)
        self.assertTrue(new.playing)

    def test_same_file_fading_out(self):
        """Test that a file fading out can be played again."""
        old = self.music.play("area25.ogg")
        old.fade_out(2)
        new = self.music.play("area25.ogg")
        self.assertIsNot(new, old)

    def test_stop(self):
        """Test stopping a channel, with and without its fade."""
        sound = self.music.play("area25.ogg")
        self.music.stop()
        self.assertTrue(sound.fading_out)
        self.assertIsNone(self.music.filename)
        sound = self.music.play("area25.ogg")
        self.music.stop(fade=0)
        self.assertTrue(sound.stopped)

    def test_volume_and_pan(self):
        """Test that the channel volume and pan are the sound's."""
        self.assertIsNone(self.music.volume)
        self.music.volume = 50
        sound = self.music.play("area25.ogg", volume=70)
        self.music.volume = 40
        self.music.pan = -20
        self.assertEqual((sound.volume, sound.pan), (40, -20))
        self.assertEqual(self.music.volume, 40)
