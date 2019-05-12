import os

from misc.helpers import exec_in_folder, run_shell_command
from misc.printer import print_warning, print_error
from . import action


class Readme(action.Action):
    def should_run(self, key):
        return key == 'r' or key == 'R'

    def run(self, login, login_path, project, project_path):
        if exec_in_folder(login_path,
                          run_shell_command, "find . -type f -iname '*README*' | egrep '.*'") is not 0:
            print_error('README not found')
        else:
            exec_in_folder(login_path,
                           run_shell_command, "find . -type f -iname '*README*' -exec less {} \\;")

    def __str__(self):
        return "R: README"
