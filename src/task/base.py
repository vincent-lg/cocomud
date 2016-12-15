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

Here's a very short example:

import time

from task.base import BaseTask
from ui.dialogs.task import TaskDialog

class Wait(BaseTask):

    "Task to wait a few seconds."

    def __init__(self):
        BaseTask.__init__(self)
        self.dialog = TaskDialog(self, "Wait for...")

    def execute(self):
        "Wait for several seconds."
        self.update(title="Waiting...")
        time.sleep(2)
        i = 0
        while i < 100:
            self.update(text="i = {}".format(i), progress=i)
            time.sleep(1)
            i += 1

And to use this class:

wait = Wait()
wait.start()
# That will pause the program and display the dialog with the progress
# bar.  The dialog will be destroyed when the task is complete or if
# the user clicks on the Cancel button.
print "After the task is finished or cancelled."

"""

from threading import Thread

from log import task as logger

class BaseTask(Thread):

    """Base class for asynchronous tasks."""

    current_id = 1

    def __init__(self):
        Thread.__init__(self)
        self._id = type(self).current_id
        type(self).current_id += 1
        self.dialog = None
        self.cancelled = False

    def __repr__(self):
        return "<Task {}>".format(self.task_id)

    def __str__(self):
        return self.task_id

    @property
    def task_id(self):
        """Return a str identifying the task."""
        return "{}[{}]".format(type(self).__name__, self._id)

    def check_active(self):
        """Check if active.

        If the task has been cancelled, raise InterruptedTask.

        """
        if self.cancelled:
            raise InterruptTask

    def start(self):
        """Start the thread and display the dialog."""
        logger.debug("Starting the task {}".format(self))
        Thread.start(self)
        if self.dialog:
            self.dialog.ShowModal()

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
        else:
            logger.debug("Completed the task {} successfully".format(self))
        finally:
            if self.dialog:
                self.dialog.Destroy()

    def cancel(self):
        """Should a specific action be performed when cancelled?"""
        logger.debug("Cancelled the task {}".format(self))

    def update(self, title=None, text=None, progress=None):
        """Update the dialog, if any.

        Update the dialog with the specified information.  The
        information (title, text and progress) do not have to all
        be specified.  It is recommended to use this method with the
        keyword arguments:
            task.update(text="Almost done", progress=95)

        """
        self.check_active()
        if self.dialog:
            if title is not None:
                self.dialog.UpdateTitle(title)
            if text is not None:
                self.dialog.UpdateText(text)
            if progress is not None:
                self.dialog.UpdateProgress(progress)

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
