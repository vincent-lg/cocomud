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

"""Module containing the SharpEngine class."""

from textwrap import dedent

from sharp import FUNCTIONS

class SharpScript(object):

    """Class representing a SharpScript engine.

    An SharpScript engine is often linked with the game's main engine
    and an individual client, which is itself optionally linked to
    the ui application.

    """

    id = 0
    def __init__(self, engine, client, world):
        self.id = type(self).id + 1
        type(self).id += 1
        self.engine = engine
        self.client = client
        self.world = world
        self.globals = dict(globals())
        self.locals = {}
        self.functions = {}
        if engine:
            self.logger = engine.create_logger("sharp")
            self.logger.debug("Creating SharpScript #{}".format(self.id))
        else:
            self.logger = None

        # Adding the functions
        for name, function in FUNCTIONS.items():
            function.name = name
            function = function(engine, client, self, world)
            self.functions[name] = function
            self.globals[name] = function.run

    def execute(self, code, debug=False):
        """Execute the SharpScript code given as an argument."""
        if isinstance(code, basestring):
            instructions = self.feed(code)
        else:
            instructions = [code]

        globals = self.globals
        locals = self.locals
        if debug:
            print "exec", instructions

        for instruction in instructions:
            exec(instruction, globals, locals)

    def feed(self, content):
        """Feed the SharpScript engine with a string content.

        The content is probably a file with several statements in
        SharpScript, or a single statement.  In all cases, this function
        returns the list of Python codes corresponding with
        this suite of statements.

        """
        # Execute Python code if necessary
        codes = []
        while content.startswith("{+"):
            end = self.find_right_brace(content)
            code = content[2:end - 1].lstrip("\n").rstrip("\n ")
            code = repr(dedent(code)).replace("\\n", "\n")
            code = "compile(" + code + ", 'SharpScript', 'exec')"
            codes.append(code)
            content = content[end + 1:]

        # The remaining must be SharpScript, splits into statements
        statements = self.split_statements(content)
        for statement in statements:
            pycode = self.convert_to_python(statement)
            codes.append(pycode)

        return codes

    def convert_to_python(self, statement):
        """Convert the statement to Python and return the str code.

        The statement given in argument should be a tuple:  The first
        argument of the tuple should be a function (like '#play' or
        '#send').  The remaining arguments should be put in a string,
        except for other Sharp or Python code.

        """
        function_name = statement[0][1:].lower()
        arguments = []
        kwargs = {}
        for argument in statement[1:]:
            if argument.startswith("{+"):
                argument = argument[2:-1].lstrip("\n").rstrip("\n ")
                argument = repr(dedent(argument)).replace("\\n", "\n")
                argument = "compile(" + argument + ", 'SharpScript', 'exec')"
            elif argument.startswith("{"):
                argument = repr(argument[1:-1])
                argument = self.replace_semicolons(argument)
            elif argument[0] in "-+":
                kwargs[argument[1:]] = True if argument[0] == "+" else False
                continue
            else:
                argument = repr(argument)
                argument = self.replace_semicolons(argument)

            arguments.append(argument)

        code = function_name + "(" + ", ".join(arguments)
        if arguments and kwargs:
            code += ", "

        code += ", ".join([name + "=" + repr(value) for name, value in \
                kwargs.items()])

        return code + ")"

    def split_statements(self, content):
        """Split the given string content into different statements.

        A statement is one-line short at the very least.  It can be
        longer by that, if it's enclosed into braces.

        """
        statements = []
        i = 0
        function_name = ""
        arguments = []
        while True:
            remaining = content[i:]

            # If remaining is empty, saves the statement and exits the loop
            if not remaining or remaining.isspace():
                if function_name:
                    statements.append((function_name, ) + tuple(arguments))

                break

            # If remaining begins with a new line
            if remaining[0] == "\n":
                if function_name:
                    statements.append((function_name, ) + tuple(arguments))
                    function_name = ""
                    arguments = []

                i += 1
                continue

            # If remaining begins with a space
            if remaining[0].isspace():
                remaining = remaining[1:]
                i += 1
                continue

            # If the function_name is not defined, take the first parameter
            if not function_name:
                if remaining.startswith("#") and not remaining.startswith(
                        "##"):
                    # This is obviously a function name
                    function_name = remaining.splitlines()[0].split(" ")[0]
                    arguments = []
                    i += len(function_name)
                else:
                    function_name = "#send"
                    argument = remaining.splitlines()[0]
                    i += len(argument)

                    if argument.startswith("##"):
                        argument = argument[1:]

                    arguments = [argument]
            elif remaining[0] == "{":
                end = self.find_right_brace(remaining)
                argument = remaining[:end + 1]
                i += end + 1
                if argument.startswith("##"):
                    argument = argument[1:]

                arguments.append(argument)
            else:
                argument = remaining.splitlines()[0].split(" ")[0]
                i += len(argument)
                if argument.startswith("##"):
                    argument = argument[1:]

                arguments.append(argument)

        return statements

    def find_right_brace(self, text):
        """Find the right brace matching the opening one.

        This function doesn't only look for the first right brace (}).
        It looks for a brace that would close the text and return the
        position of this character.  For instance:
            >>> Engine.find_right_brace("{first parameter {with} something} else")
            33

        """
        level = 0
        i = 0
        while i < len(text):
            char = text[i]
            if char == "{":
                level += 1
            elif char == "}":
                level -= 1

            if level == 0:
                return i

            i += 1

        return None

    @staticmethod
    def replace_semicolons(text):
        """Replace all not-escaped semi-colons."""
        i = 0
        while i < len(text):
            remaining = text[i:]
            if remaining.startswith(";;"):
                i += 2
                continue
            elif remaining.startswith(";"):
                text = text[:i] + "\n" + text[i + 1:]
            i += 1

        return text.replace(";;", ";")

    def format(self, content, return_str=True):
        """Write SharpScript and return a string.

        This method takes as argument the SharpScript content and formats it.  It therefore replaces the default formatting.  Arguments are escaped this way:

        * If the argument contains space, escape it with braces.
        * If the argument contains new line, indent it.
        * If the argument contains semi colons, keep it on one line.

        """
        if isinstance(content, basestring):
            instructions = self.split_statements(content)
        else:
            instructions = content

        # At this stage, the instructions are formatted in Python
        lines = []
        for arguments in instructions:
            function = arguments[0].lower()
            arguments = list(arguments[1:])

            # Escape the arguments if necessary
            for i, argument in enumerate(arguments):
                arguments[i] = self.escape_argument(argument)

            line = function + " " + " ".join(arguments)
            lines.append(line.rstrip(" "))

        return "\n".join(lines) if return_str else lines

    @staticmethod
    def escape_argument(argument):
        """Escape the argument if needed."""
        if argument.startswith("{"):
            pass
        elif "\n" in argument:
            lines = argument.splitlines()
            argument = "{\n    " + "\n    ".join(lines) + "\n}"
        elif " " in argument:
            argument = "{" + argument + "}"

        return argument

    def extract_arguments(self, line):
        """Extract the funciton name and arguments.

        This function returns a tuple of three informations:

        * The funciton name (a string)
        * A list of arguments (all strings)
        * A dictionary of flags (True or False as values)

        """
        instructions = self.split_statements(line)
        line = instructions[0]
        function = line[0]
        arguments = []
        flags = {}

        # Browse through the list of arguments
        for argument in line[1:]:
            if argument[0] in "-+":
                flag = argument[1:].lower()
                if argument[0] == "-":
                    flags[flag] = False
                else:
                    flags[flag] = True
                continue
            elif argument.startswith("{"):
                argument = argument[1:-1]
                if "\n" in argument:
                    argument = dedent(argument.strip("\n"))

            arguments.append(argument)

        return function, arguments, flags
