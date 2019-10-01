import os

from helpers.autocomplete import CmdCompletor, enum_tp_slugs, enum_logins_for_tp, enum_files
from helpers.io import folder_remove
from misc.printer import print_success, print_info, print_error
from misc.config import EXIT_SUCCESS, EXIT_FAILURE
from misc.data import Tp, Submission


def cmd_remove(tp_slug, logins, remove_all, remove_moulinette):
    """
    Remove the students repo corresponding to the given TP slug
    :param tp_slug: Slug of the TP to remove
    :param logins: List of student logins
    :param remove_all: Should all the students files be removed
    :param remove_moulinette: Should the moulinette be removed
    """
    success = True
    tp = Tp(tp_slug)
    if not tp.has_local_submissions():
        print_error("TP " + tp_slug + " not found")
    else:
        if remove_all or len(logins) is 0:
            tp.remove_locally()
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
                        repo.remove_locally()
                        print_success('')
                    except IOError:
                        print_error('')
                        success = False
                        continue
                else:
                    print_error('')

    if remove_moulinette:
        tp.remove_moulinette_locally()

    return EXIT_SUCCESS if success else EXIT_FAILURE


CPLT = CmdCompletor(
    [ '-a', '--all', '-m', '--moulinette' ],
    { '--file=': enum_files },
    [ enum_tp_slugs, enum_logins_for_tp ])

def cplt_remove(text, line, begidx, endidx):
    return CPLT.complete(text, line, begidx, endidx)
