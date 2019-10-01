import os

from helpers.autocomplete import CmdCompletor, enum_tp_slugs, enum_logins_for_tp
from helpers.io import folder_ls
from helpers.terminal import open_subshell
from misc.printer import print_error
from misc.config import EXIT_SUCCESS, EXIT_FAILURE
from misc.data import Tp, Submission


def cmd_edit(tp_slug, login):
    """
    Open a shell into the student repo
    :param tp_slug: TP slug
    :param login: Student login
    """
    repo = Submission(tp_slug, login)
    if repo.exists_locally():
        open_subshell(repo.local_dir())
        return EXIT_SUCCESS
    else:
        print_error('Repository not found locally.')
        return EXIT_FAILURE


CPLT = CmdCompletor(
    [],
    {},
    [ enum_tp_slugs, enum_logins_for_tp ])

def cplt_edit(text, line, begidx, endidx):
    return CPLT.complete(text, line, begidx, endidx)
