import os

from misc.helpers import open_subshell, exec_in_folder
from . import action


class Shell(action.Action):
    def should_run(self, key):
        return key == 's' or key == 'S'

    def run(self, login, login_path, solution, solution_path):
        exec_in_folder(os.path.join(login_path),
                       open_subshell)

    def __str__(self):
        return "S: SHELL"
