from misc.helpers import run_command
from . import action


class Next(action.Action):
    def should_run(self, key):
        return key == 's' or key == 'S'

    def run(self, login, login_path, solution, solution_path):
        run_command("cd " + solution_path + "; bash")

    def __str__(self):
        return "S: SHELL"
