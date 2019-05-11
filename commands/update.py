from misc.config import TOOLKIT_FOLDER
from misc.helpers import exec_in_folder, git_update
from misc.printer import print_success


def cmd_update():
    """
    Update the toolkit
    """
    exec_in_folder(
        TOOLKIT_FOLDER,
        git_update
    )

    print_success('Update successful!')
    # Force user to reload script
    exit()
