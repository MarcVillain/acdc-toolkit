import os

from misc.helpers import folder_find, folder_create, file_copy
from misc.printer import print_info
from . import action


class CopyFiles(action.Action):
    def should_run(self, key):
        return key is None \
            or key == 'n' or key == 'N' \
            or key == 'p' or key == 'P'

    def run(self, login, login_path, solution, solution_path):
        print_info("Copying files of " + login + " (" + solution + ")")
        files = folder_find(os.path.join(login_path, solution), includes=[".*\\.cs"], excludes=["AssemblyInfo.cs"])
        for file in files:
            src = file
            file = file[len(os.path.join(login_path, solution))+1:]
            dest = os.path.join(solution_path, file)
            folder_create(os.path.dirname(dest))
            file_copy(src, dest)
