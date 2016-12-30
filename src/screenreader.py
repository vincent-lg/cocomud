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

"""This file contains the ScreenReader class, to interact with the TTS.

This class is supposed to be platform-independent and use what is
available on that system.  To use it, one should call its 'talk' method,
which allows to speak to the screen reader.

"""

try:
    from UniversalSpeech import say
    from UniversalSpeech import braille as display_braille
except (ImportError, OSError):
    say = None
    display_braille = None

class ScreenReader:

    """Wrapper class to send messages to the screen reader.

    No need to instantiate this class.  Just use its  'talk' method.

    >>> from screenreader import ScreenReader
    >>> ScreenReader.talk("So it works")
    >>> ScreenReader.talk("But don't display that.", braille=False)

    """

    @staticmethod
    def talk(message, speech=True, braille=True, interrupt=True):
        """Send the message to the screen reader to be spoken or displayed.

        Parameters:
            message: The message to be sent (str or unicode)
            speech (default True): should htis message be spoken?
            braille (default True): should the message be displayed?

        """
        message = message.strip()
        if not message:
            return

        if say and speech:
            say(message, interrupt=interrupt)

        if braille and display_braille:
            display_braille(message)
