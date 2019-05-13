import os

from helpers.autocomplete import autocomplete
from helpers.io import folder_remove, folder_ls
from misc.config import STUDENTS_FOLDER, REPO_FOLDER
from misc.printer import print_success, print_info, print_error


def cmd_remove(tp_slug, logins):
    """
    Remove the students repo corresponding to the given TP slug
    :param tp_slug: Slug of the TP to remove
    :param logins: List of student logins
    """
    if tp_slug not in folder_ls(STUDENTS_FOLDER):
        print_error("TP " + tp_slug + " not found")
        return

    tp_folder = os.path.join(STUDENTS_FOLDER, tp_slug)

    if len(logins) is 0:
        folder_remove(tp_folder)
        print_success("Successfully removed " + tp_folder)
    else:
        for i, login in enumerate(logins):
            print_info("{tp_slug} ({login}) ".format(tp_slug=tp_slug, login=login),
                       percent_pos=i, percent_max=len(logins), end='')
            student_tp_folder = os.path.join(tp_folder, REPO_FOLDER.format(tp_slug=tp_slug, login=login))
            try:
                folder_remove(student_tp_folder)
                print_success('')
            except IOError:
                print_error('')
                continue


def cplt_remove(text, line, begidx, endidx, options):
    return autocomplete(text, line, begidx, endidx,
                        [[folder for folder in folder_ls(STUDENTS_FOLDER)
                          if 'tp' in folder]],
                        options)
