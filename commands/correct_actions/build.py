import os

from misc.helpers import exec_in_folder, run_shell_command, run_command
from misc.printer import print_error, print_success, print_info
from . import action


class Build(action.Action):
    def should_run(self, key):
        return key == 'b' or key == 'B'

    def run(self, login, login_path, project, project_path):
        print_info("Building project " + project)
        res = exec_in_folder(project_path,
                             run_command,
                             "msbuild " + os.path.join(os.path.basename(project) + ".csproj"))

        if res.returncode is not 0:
            print_error("Build failed:\n" + res.stdout + res.stderr)
        else:
            print_success("Build successful")

    def __str__(self):
        return "B: BUILD"
