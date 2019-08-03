import os

from helpers.autocomplete import autocomplete
from helpers.io import folder_ls
from misc.printer import print_info
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


def cplt_list(text, line, begidx, endidx, options):
    return autocomplete(text, line, begidx, endidx,
                        [[ tp.slug() for tp in Tp.get_local_tps() ]],
                        options)
