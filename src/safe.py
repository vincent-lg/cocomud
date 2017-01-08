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


"""This file contains the 'safe' system of CocoMUD, ways to crypt/encrypt.

This feature requires:
    pbkdf2
    Crypto

The module contains a class named 'Safe', that should be insantiated
in order to manipulate the encrypting
/decrypting mechanism.  This class requires a passphrase in
argument.  You can insantiate it as follows:
>>> from safe import Safe
>>> safe = Safe(file=".passphrase")
>>> # (If the file doesn't exist, it will be created with an auto-generated
>>> # passphrase.)
>>> # Alternatively you can specify the passphrase directly
>>> safe = Safe(passphrase="Dsm18fvdjP9sz801,9DJA.1356gndYJz987v")
>>> # Store encrypted data
>>> safe.store("login", "kredh")
>>> safe.store("password", "YoudWishIToldYou")
>>> # Retrieve the data (can be later)
login = safe.retrieve("login")
password = safe.retrieve("password")

Note that datas that is not a string (like a bool or float) will be
saved as unprotected data.  If you want to save it encrypted, you can
convert it to string.

"""

import base64
import os
import pickle

from Crypto.Cipher import AES
from pbkdf2 import PBKDF2

class Safe:

    """A safe object, to encrypt/decrypt information.

    The Safe class requires a passphrase to be created.  This is a
    string of characters that adds to the security of encryption.
    Obviously, it needs to remain similar to decrypt information that
    has been encrypted.  Other optional parameters are also possible:
        secret: the path of the file in which to store crypted data.


    """

    def __init__(self, passphrase=None, file=None, secret="data.crypt",
            load=True):
        self.salt_seed = 'mkhgts465wef4fwtdd'
        self.passphrase = passphrase
        self.secret = secret
        self.passphrase_size = 64
        self.key_size = 32
        self.block_size = 16
        self.iv_size = 16
        self.salt_size = 8
        self.data = {}

        if file and os.path.exists(file):
            with open(file, "r") as pass_file:
                self.passphrase = pass_file.read()

        if not self.passphrase:
            self.passphrase = base64.b64encode(os.urandom(
                    self.passphrase_size))
            if file:
                with open(file, "w") as pass_file:
                    pass_file.write(self.passphrase)

        # Load the secret file
        if load:
            self.load()

    def get_salt_from_key(self, key):
        return PBKDF2(key, self.salt_seed).read(self.salt_size)

    def encrypt(self, plaintext, salt):
        """Pad plaintext, then encrypt it.

        The encryption occurs with a new, randomly initialised cipher.
        This method will not preserve trailing whitespace in plaintext!.

        """
        # Initialise Cipher Randomly
        init_vector = os.urandom(self.iv_size)

        # Prepare cipher key
        key = PBKDF2(self.passphrase, salt).read(self.key_size)
        cipher = AES.new(key, AES.MODE_CBC, init_vector)

        bs = self.block_size
        return init_vector + cipher.encrypt(plaintext + \
                " " * (bs - (len(plaintext) % bs)))

    def decrypt(self, ciphertext, salt):
        """Reconstruct the cipher object and decrypt.

        This method will not preserve trailing whitespace in the
        retrieved value.

        """
        # Prepare cipher key
        key = PBKDF2(self.passphrase, salt).read(self.key_size)

        # Extract IV
        init_vector = ciphertext[:self.iv_size]
        ciphertext = ciphertext[self.iv_size:]

        cipher = AES.new(key, AES.MODE_CBC, init_vector)

        return cipher.decrypt(ciphertext).rstrip(" ")

    def load(self):
        """Load the data from the 'secret' file if exists."""
        if os.path.exists(self.secret):
            with open(self.secret, "rb") as file:
                upic = pickle.Unpickler(file)
                self.data = upic.load()
                if not isinstance(self.data, dict):
                    raise ValueError("the data contained in the file " \
                            "'{}' is not a dictionary".format(self.secret))

    def retrieve(self, key, *default):
        """Retrieve and decrypt the specified key.

        If the key isn't present in the dictionary, either
        return default if specified, or raise a KeyError.

        If the value at this location isn't a string, return it as is.

        """
        if key not in self.data:
            if default:
                return default[0]

            raise KeyError(key)

        value = self.data[key]
        if isinstance(value, basestring):
            salt = self.get_salt_from_key(key)
            return self.decrypt(value, salt)

        return value

    def store(self, key, value):
        """Store the key in the file.

        If the key already exists, replaces it.
        If the value is not a string or unicode, it will be stored
        WITHOUT encryption.

        """
        if isinstance(value, basestring):
            salt = self.get_salt_from_key(key)
            crypted = self.encrypt(value, salt)
            self.data[key] = crypted
        else:
            self.data[key] = value

        # Write the new data in the file
        with open(self.secret, "wb") as file:
            pic = pickle.Pickler(file)
            pic.dump(self.data)
