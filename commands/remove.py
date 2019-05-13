import os

from helpers.io import folder_remove
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
