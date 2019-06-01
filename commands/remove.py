import os

from helpers.autocomplete import autocomplete
from helpers.io import folder_remove, folder_ls
from misc.config import STUDENTS_FOLDER, REPO_FOLDER, MOULINETTE_FOLDER
from misc.printer import print_success, print_info, print_error


def cmd_remove(tp_slug, logins, remove_all, remove_moulinette):
    """
    Remove the students repo corresponding to the given TP slug
    :param tp_slug: Slug of the TP to remove
    :param logins: List of student logins
    :param remove_all: Should all the students files be removed
    :param remove_moulinette: Should the moulinette be removed
    """
    if tp_slug not in folder_ls(STUDENTS_FOLDER):
        print_error("TP " + tp_slug + " not found")
    else:
        tp_folder = os.path.join(STUDENTS_FOLDER, tp_slug)

        if remove_all or len(logins) is 0:
            folder_remove(tp_folder)
            print_success("Successfully removed " + tp_slug)
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

    if remove_moulinette:
        moulinette_folder = os.path.join(MOULINETTE_FOLDER, tp_slug)
        try:
            folder_remove(moulinette_folder)
            print_success("Successfully removed moulinette " + tp_slug)
        except IOError:
            print_error("Moulinette " + tp_slug + " not found")


def cplt_remove(text, line, begidx, endidx, options):
    return autocomplete(text, line, begidx, endidx,
                        [[folder for folder in folder_ls(STUDENTS_FOLDER)
                          if 'tp' in folder]],
                        options)
