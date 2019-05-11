from misc.helpers import folder_find, files_remove
from misc.printer import print_info
from . import action


class ClearFiles(action.Action):
    def should_run(self, key):
        return key is None \
            or key == 'n' or key == 'N' \
            or key == 'p' or key == 'P'

    def run(self, login, login_path, solution, solution_path):
        print_info("Clearing files of solution " + solution)
        files = folder_find(solution_path, includes=[".*\\.cs"], excludes=["AssemblyInfo.cs", solution + "Tests"])
        files_remove(files)
