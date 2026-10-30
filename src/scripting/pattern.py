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

"""Module converting trigger and alias patterns to regular expressions."""

import re

def pattern_to_regex(pattern):
    """Convert a pattern to a regular expression (str).

    In a pattern, '*' matches any text and becomes a group.  A
    backslash makes the next character literal:  '\\*' is an asterisk,
    '\\\\' a backslash and '\\^' (at the beginning) a caret, since a
    pattern beginning with '^' is already a regular expression.

    The regular expression must match the entire line.

    """
    regex = ""
    i = 0
    while i < len(pattern):
        char = pattern[i]
        if char == "\\" and i + 1 < len(pattern):
            i += 1
            regex += re.escape(pattern[i])
        elif char == "*":
            regex += "(.*?)"
        else:
            regex += re.escape(char)

        i += 1

    return "^" + regex + "$"

def unwrap_python(pattern):
    """Return the pattern without the Python braces, if any.

    Older versions saved a pattern beginning with '+' and containing
    spaces as '{+...}', which is read as Python code.  A pattern is
    never Python code, so it is restored here.

    """
    if pattern.startswith("{+") and pattern.endswith("}"):
        pattern = pattern[1:-1]

    return pattern
