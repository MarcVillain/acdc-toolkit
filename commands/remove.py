import os

from helpers.autocomplete import autocomplete
from helpers.io import folder_remove, folder_ls
from misc.config import STUDENTS_FOLDER
from misc.printer import print_success


def cmd_remove(tp_slug):
    """
    Remove the students repo corresponding to the given TP slug
    :param tp_slug: Slug of the TP to download
    """
    tp_folder = os.path.join(STUDENTS_FOLDER, tp_slug)
    folder_remove(tp_folder)
    print_success('Successfully removed ' + tp_slug)


def cplt_remove(text, line, begidx, endidx, options):
    return autocomplete(text, line, begidx, endidx,
                        [[folder for folder in folder_ls(STUDENTS_FOLDER)
                          if 'tp' in folder]],
                        options)
