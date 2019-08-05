import os

from helpers.autocomplete import CmdCompletor, enum_tp_slugs
from helpers.io import folder_ls
from misc.printer import print_info
from misc.config import EXIT_SUCCESS
from misc.data import Tp, Submission


def cmd_list(tp_slug):
    """
    List all the downloaded repos
    :param tp_slug: TP slug
    """
    if tp_slug is None:
        for tp in Tp.get_local_tps():
            print_info(tp.slug())
    else:
        tp = Tp(tp_slug)
        for repo in tp.get_local_submissions():
            print_info(repo.login())
    return EXIT_SUCCESS


CPLT = CmdCompletor(
    [],
    {},
    [ enum_tp_slugs ])

def cplt_list(text, line, begidx, endidx):
    return CPLT.complete(text, line, begidx, endidx)
