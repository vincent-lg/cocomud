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

from unittest import TestCase
import os, shutil

from safe import Safe

class SafeTests(TestCase):
    "Test for the `Safe` class"

    # Files used by the safe class
    base_dir = os.path.join(os.path.abspath("."), "test_safe_data")
    pass_file = os.path.join(base_dir, ".passphrase")
    secret_file = os.path.join(base_dir, "data.secret")

    def setUp(self):
        "Sets up the test case"

        # The `Safe` object needs two files and we put these inside a folder.
        os.makedirs(self.base_dir)

        # We cannot ensure that all data will be removed.
        self.addCleanup(shutil.rmtree, self.base_dir, ignore_errors=True)
        self.safe = Safe(file=self.pass_file, secret=self.secret_file)

    def tearDown(self):
        "Destroys all data produced by the tests"
        if self.safe:
            self.safe = None

    def test_encrypt(self):
        "Tests if encrypt/decrypt works correctly"

        salt = self.safe.get_salt_from_key("mykey")
        value = "Decrypted value"
        encrypted = self.safe.encrypt(value, salt)

        self.assertEqual(self.safe.decrypt(encrypted, salt), value)

    def test_store(self):
        "Checks if the store/retrieve functions work correctly"

        key, value = ("mykey", "myvalue")
        self.safe.store(key, value)
        self.assertEqual(self.safe.retrieve(key), value)

