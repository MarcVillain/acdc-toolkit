import os

from helpers.autocomplete import CmdCompletor, enum_tp_slugs, enum_logins_for_tp, enum_files
from helpers.io import folder_remove
from misc.printer import print_success, print_info, print_error
from misc.data import Tp, Submission


def cmd_remove(tp_slug, logins, remove_all, remove_moulinette):
    """
    Remove the students repo corresponding to the given TP slug
    :param tp_slug: Slug of the TP to remove
    :param logins: List of student logins
    :param remove_all: Should all the students files be removed
    :param remove_moulinette: Should the moulinette be removed
    """
    tp = Tp(tp_slug)
    if not os.path.exists(tp.local_dir()):
        print_error("TP " + tp_slug + " not found")
    else:
        if remove_all or len(logins) is 0:
            folder_remove(tp.local_dir())
            print_success("Successfully removed " + tp_slug)
        else:
            for i, login in enumerate(logins):
                repo = Submission(tp, login)
                print_info(
                    "{tp_slug} ({login}) ".format(
                        tp_slug=repo.tp().slug(),
                        login=repo.login()),
                    percent_pos=i, percent_max=len(logins), end='')
                if repo.exists_locally():
                    try:
                        folder_remove(repo.local_dir())
                        print_success('')
                    except IOError:
                        print_error('')
                        continue
                else:
                    print_error('')


    if remove_moulinette:
        try:
            folder_remove(tp.local_moulinette_dir())
            print_success("Successfully removed moulinette " + tp_slug)
        except IOError:
            print_error("Moulinette " + tp_slug + " not found")


CPLT = CmdCompletor(
    [ '-a', '--all', '-m', '--moulinette' ],
    { '--file=': enum_files },
    [ enum_tp_slugs, enum_logins_for_tp ])

def cplt_remove(text, line, begidx, endidx):
    return CPLT.complete(text, line, begidx, endidx)
