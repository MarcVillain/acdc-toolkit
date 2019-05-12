from misc.helpers import exec_in_folder, run_shell_command
from . import action


class Log(action.Action):
    def should_run(self, key):
        return key == 'l' or key == 'L'

    def run(self, login, login_path, solution, solution_path):
        exec_in_folder(login_path,
                       run_shell_command, "git log --color=always | less -R")

    def __str__(self):
        return "L: GIT LOG"
