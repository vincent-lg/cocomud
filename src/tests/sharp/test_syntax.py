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

import unittest

from sharp.engine import SharpScript

class TestSyntax(unittest.TestCase):

    """Unittest for the SharpScript syntax."""

    def setUp(self):
        """Create the SharpScript instance."""
        self.engine = SharpScript(None, None, None)

    def test_single(self):
        """Test a single statement."""
        # Test a statement on one line with one argument
        statements = self.engine.feed("#play file.wav")
        self.assertEqual(statements, ["play('file.wav')"])

        # Test a statement with an new line and no argument
        statements = self.engine.feed("#stop\n")
        self.assertEqual(statements, ["stop()"])

        # Same test, but with some useless spaces
        statements = self.engine.feed("  #stop  \n  ")
        self.assertEqual(statements, ["stop()"])

        # Test a statement with arguments surrounded by braces
        statements = self.engine.feed("#macro {Alt + Enter} north")
        self.assertEqual(statements, ["macro('Alt + Enter', 'north')"])

        # Same test but with some useless spaces
        statements = self.engine.feed("  #macro  {Alt + Enter}  north\n  ")
        self.assertEqual(statements, ["macro('Alt + Enter', 'north')"])

        # Test what happens without function names
        statements = self.engine.feed("say Hello all!\n  ")
        self.assertEqual(statements, ["send('say Hello all!')"])

    def test_multiple(self):
        """Test multiple statements at once."""
        # Test two statements on two lines without useless spaces
        statements = self.engine.feed("#play file.wav\n#stop")
        self.assertEqual(statements, ["play('file.wav')", "stop()"])

        # Same test, but with some useless spaces
        statements = self.engine.feed("  #play   file.wav  \n#stop  \n  ")
        self.assertEqual(statements, ["play('file.wav')", "stop()"])

    def test_python(self):
        """Test Python syntax embeeded in SharpScript."""
        statements = self.engine.feed("""#trigger {Should it work?} {+
            var = 2 + 3
            print var
        }""")
        self.assertEqual(statements, [
            "trigger('Should it work?', compile('var = 2 + 3\nprint var', " \
            "'SharpScript', 'exec'))"
        ])

    def test_flag(self):
        """Test the SharpScript syntax with flags in funciton calls."""
        statements = self.engine.feed("#say {A message} -braille +speech")
        self.assertEqual(statements, [
            "say('A message', braille=False, speech=True)"
        ])

    def test_python_top(self):
        """Test Python code in SharpScript at the top level."""
        statements = self.engine.feed("""{+
            print 1
            print 3
        }""")
        self.assertEqual(statements, [
            "compile('print 1\nprint 3', 'SharpScript', 'exec')",
        ])

    def test_semicolons(self):
        """Test the semi-colons."""
        # A test with simple text
        statements = self.engine.feed("#macro F1 north;south;;east")
        self.assertEqual(statements, ["macro('F1', 'north\nsouth;east')"])

        # A test with SharpScript
        statements = self.engine.feed("#trigger ok {#play new.wav;#stop}")
        self.assertEqual(statements, [
                "trigger('ok', '#play new.wav\n#stop')",
        ])

    def test_escape_sharp(self):
        """Test the escaped sharp symbol."""
        # A sharp escaping with plain text
        statements = self.engine.feed("##out")
        self.assertEqual(statements, ["send('#out')"])

        # A sharp escaping with SharpScript
        statements = self.engine.feed("#macro ##ok")
        self.assertEqual(statements, ["macro('#ok')"])
