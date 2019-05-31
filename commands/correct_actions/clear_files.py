import os

from helpers.io import folder_find, files_remove
from misc.printer import print_info
from . import action


class ClearFiles(action.Action):
    def should_run(self, key):
        return key is None \
            or key == 'n' or key == 'N' \
            or key == 'p' or key == 'P' \
            or key == 'f' or key == 'F'

    def run(self, login, login_path, project, project_path):
        print_info("Clearing files of project " + project)
        files = folder_find(project_path, includes=[".*\\.cs"],
                            excludes=["AssemblyInfo.cs"])
        files_remove(files)
