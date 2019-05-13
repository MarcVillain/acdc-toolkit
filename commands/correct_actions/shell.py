import os

from helpers.command import exec_in_folder, run_shell_command
from helpers.terminal import open_subshell
from misc.printer import print_warning, print_error
from . import action


class Shell(action.Action):
    def should_run(self, key):
        return key == 's' or key == 'S'

    def run(self, login, login_path, project, project_path):
        open_subshell(login_path)

    def __str__(self):
        return "S: SHELL"
