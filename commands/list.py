import os

from helpers.autocomplete import autocomplete
from helpers.io import folder_ls
from misc.config import STUDENTS_FOLDER
from misc.printer import print_info


def cmd_list(tp_slug):
    """
    List all the downloaded repos
    :param tp_slug: TP slug
    """
    for folder in folder_ls(STUDENTS_FOLDER):
        if tp_slug:
            if folder == tp_slug:
                for subfolder in folder_ls(os.path.join(STUDENTS_FOLDER, folder)):
                    subfolder = subfolder.replace(folder + "-", "")
                    print_info(subfolder)
        else:
            print_info(folder)


def cplt_list(text, line, begidx, endidx, options):
    return autocomplete(text, line, begidx, endidx,
                        [[folder for folder in folder_ls(STUDENTS_FOLDER)
                          if 'tp' in folder]],
                        options)
