import os

from helpers.io import folder_find, folder_create, file_copy, file_insert_text_every_n_lines
from misc.printer import print_info
from . import action


class CopyFiles(action.Action):
    def should_run(self, key):
        return key is None \
            or key == 'n' or key == 'N' \
            or key == 'p' or key == 'P' \
            or key == 'f' or key == 'F'

    def run(self, login, login_path, project, project_path):
        print_info("Copying files of " + login + " (" + project + ")")
        student_project_folder = os.path.join(login_path, project)
        files = folder_find(student_project_folder, includes=[".*\\.cs", ".*\\.csproj"], excludes=["AssemblyInfo.cs"])
        for file in files:
            src = file
            dest = os.path.join(project_path, file[len(student_project_folder)+1:])
            folder_create(os.path.dirname(dest))
            file_copy(src, dest)
            if file.endswith(".cs"):
                file_insert_text_every_n_lines(dest, "// " + login, 20)
