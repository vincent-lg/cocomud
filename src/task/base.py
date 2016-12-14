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

"""Module containing the BaseTask class.

A task is an operation run in an independent thread.  It can be bond
to a dialog box with a progress bar.  This can be useful to report
progress in a foreground task.

See the other modules in this package for examples.

"""

from threading import Thread

class BaseTask(Thread):

    """Base class for asynchronous tasks."""

    def __init__(self):
        Thread.__init__(self)
        self.window = None
        self.cancelled = False

    def check_active(self):
        """Check if active.

        If the task has been cancelled, raise InterruptedTask.

        """
        if self.cancelled:
            raise InterruptTask

    def run(self):
        """Run in a separate thread.

        This method will call 'execute' in a separate thread and
        will catch specific exceptions.  It shouldn't be necessary
        to override this method.

        """
        try:
            self.execute()
        except InterruptTask:
            self.cancel()
        finally:
            if self.window:
                self.window.Destroy()

    def cancel(self):
        """Should a specific action be performed when cancelled?"""
        print "Task", self, "interrupted"

    def execute(self):
        """Execute the task.

        Override this class to define the task's behavior.

        """
        raise NotImplementedError


class InterruptTask(RuntimeError):

    """The task is interrupted.

    This can happen when the user has clicked on 'cancel', or another
    signal has been received to terminate the task.

    """

    pass
