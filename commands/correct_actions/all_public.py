from misc.helpers import folder_find, files_remove, file_replace
from misc.printer import print_info
from . import action


class AllPublic(action.Action):
    def should_run(self, key):
        return key is None \
            or key == 'n' or key == 'N' \
            or key == 'p' or key == 'P'

    def run(self, login, login_path, project, project_path):
        print_info("Replacing all private/protected/... with public")

        replace_table = {
            "private": "public",
            "protected": "public",
            "internal": "public",
            "public set": "public",
            "Main": "StudentMain",
        }

        for file in folder_find(project_path, includes=[".*\\.cs"], excludes=["AssemblyInfo.cs"]):
            for text_to_search, replacement_text in replace_table.items():
                file_replace(file, text_to_search, replacement_text)
