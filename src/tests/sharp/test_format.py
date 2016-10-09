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

from textwrap import dedent
import unittest

from sharp.engine import SharpScript

class TestFormat(unittest.TestCase):

    """Unittest for the SharpScript format."""

    def setUp(self):
        """Create the SharpScript instance."""
        self.engine = SharpScript(None, None, None)

    def test_single(self):
        """Test a single statement."""
        # Test a statement on one line with one argument
        content = self.engine.format("#play file.wav")
        self.assertEqual(content, "#play file.wav")

        # Test a statement with an new line and no argument
        content = self.engine.format("#stop\n")
        self.assertEqual(content, "#stop")

        # Same test, but with some useless spaces
        content = self.engine.format("  #stop  \n  ")
        self.assertEqual(content, "#stop")

        # Test a statement with arguments surrounded by braces
        content = self.engine.format("#macro {Alt + Enter} north")
        self.assertEqual(content, "#macro {Alt + Enter} north")

        # Same test but with some useless spaces
        content = self.engine.format("  #macro  {Alt + Enter}  north\n  ")
        self.assertEqual(content, "#macro {Alt + Enter} north")

        # Test what happens without function names
        content = self.engine.format("say Hello all!\n  ")
        self.assertEqual(content, "#send {say Hello all!}")

    def test_multiple(self):
        """Test multiple statements at once."""
        # Test two statements on two lines without useless spaces
        content = self.engine.format("#play file.wav\n#stop")
        self.assertEqual(content, "#play file.wav\n#stop")

        # Same test, but with some useless spaces
        content = self.engine.format("  #play   file.wav  \n#stop  \n  ")
        self.assertEqual(content, "#play file.wav\n#stop")

    def test_python(self):
        """Test Python format embeeded in SharpScript."""
        content = self.engine.format(dedent("""
        #trigger {Should it work?} {+
            var = 2 + 3
            print var
        }""".strip("\n")))
        self.assertEqual(content, dedent("""
        #trigger {Should it work?} {+
            var = 2 + 3
            print var
        }""".strip("\n")))

    def test_flag(self):
        """Test the SharpScript format with flags in funciton calls."""
        content = self.engine.format("#say {A message} -braille +speech")
        self.assertEqual(content, "#say {A message} -braille +speech")

    def test_semicolons(self):
        """Test the semi-colons."""
        # A test with simple text
        content = self.engine.format("#macro F1 north;south;;east")
        self.assertEqual(content, "#macro F1 north;south;;east")

        # A test with SharpScript
        content = self.engine.format("#trigger ok {#play new.wav;#stop}")
        self.assertEqual(content, "#trigger ok {#play new.wav;#stop}")

    def test_escape_sharp(self):
        """Test the escaped sharp symbol."""
        # A sharp escaping with plain text
        content = self.engine.format("##out")
        self.assertEqual(content, "#send #out")
