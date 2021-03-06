from helpers.io import folder_find, file_replace
from misc.printer import print_info
from . import action


class AllPublic(action.Action):
    def should_run(self, key):
        return key is None \
            or key == 'n' or key == 'N' \
            or key == 'p' or key == 'P' \
            or key == 'f' or key == 'F'

    def run(self, login, login_path, project, project_path):
        print_info("Replacing all private/protected/... with public")

        replace_table = {
            "private": "public",
            "protected": "public",
            "internal": "public",
            "public set": "set",
        }

        for file in folder_find(project_path, includes=[".*\\.cs"], excludes=["AssemblyInfo.cs"]):
            for text_to_search, replacement_text in replace_table.items():
                file_replace(file, text_to_search, replacement_text)
