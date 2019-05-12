import os

from misc.helpers import exec_in_folder, run_shell_command
from misc.printer import print_warning
from . import action


class Shell(action.Action):
    def should_run(self, key):
        return key == 's' or key == 'S'

    def run(self, login, login_path, solution, solution_path):
        print()
        print_warning('Press Ctrl+D to get back.')
        print()

        exec_in_folder(os.path.join(login_path),
                       run_shell_command, "bash")

    def __str__(self):
        return "S: SHELL"
