import os

from helpers.autocomplete import autocomplete, get_arg_number, get_arg_value, parse_args
from helpers.io import folder_ls
from helpers.terminal import open_subshell
from helpers.students import get_downloaded_students
from misc.config import STUDENTS_FOLDER, REPO_FOLDER


def cmd_edit(tp_slug, login):
    """
    Open a shell into the student repo
    :param tp_slug: TP slug
    :param login: Student login
    """
    open_subshell(os.path.join(STUDENTS_FOLDER, tp_slug, REPO_FOLDER.format(tp_slug=tp_slug, login=login)))


def cplt_edit(text, line, begidx, endidx, options):
    args = parse_args(line)
    number = get_arg_number(args, begidx)
    arguments = [[folder for folder in folder_ls(STUDENTS_FOLDER)
                         if 'tp' in folder]]
    if number > 1:
        arguments.append(get_downloaded_students(args[1][0]))
    return autocomplete(text, line, begidx, endidx,
                        arguments, options)
