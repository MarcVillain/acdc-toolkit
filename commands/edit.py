import os

from helpers.autocomplete import autocomplete, get_arg_number, get_arg_value, parse_args
from helpers.io import folder_ls
from helpers.terminal import open_subshell
from misc.printer import print_error
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
    else:
        print_error('Repository not found locally.')


def cplt_edit(text, line, begidx, endidx, options):
    args = parse_args(line)
    number = get_arg_number(args, begidx)
    arguments = [[ tp.slug() for tp in Tp.get_local_tps() ]]
    if number > 1:
        arguments.append([ sub.login()
                           for sub in Tp(args[1][0]).get_local_submissions() ])
    return autocomplete(text, line, begidx, endidx,
                        arguments, options)
