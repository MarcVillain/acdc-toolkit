import os

from misc.helpers import exec_in_folder, run_shell_command
from . import action


class Tree(action.Action):
    def should_run(self, key):
        return key == 't' or key == 'T'

    def run(self, login, login_path, solution, solution_path):
        exec_in_folder(login_path,
                       run_shell_command,
                       "tree " + os.path.join("..", os.path.basename(login_path)) + " -aC -I '.git' | less -R")

    def __str__(self):
        return "T: TREE"
