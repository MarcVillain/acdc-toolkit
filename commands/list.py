import os

from helpers.io import folder_ls
from misc.config import STUDENTS_FOLDER
from misc.printer import print_info


def cmd_list(display_detail):
    """
    List all the downloaded repos
    :param display_detail If we should list students on each folder or not
    """
    for folder in folder_ls(STUDENTS_FOLDER):
        if 'tp' in folder:
            print_info(folder)
            if display_detail:
                for subfolder in folder_ls(os.path.join(STUDENTS_FOLDER, folder)):
                    subfolder = subfolder.replace(folder + "-", "")
                    print_info(subfolder, 1)
