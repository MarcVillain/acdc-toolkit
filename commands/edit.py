import os

from helpers.terminal import open_subshell
from misc.config import STUDENTS_FOLDER, REPO_FOLDER


def cmd_edit(tp_slug, login):
    """
    Open a shell into the student repo
    :param tp_slug: TP slug
    :param login: Student login
    """
    open_subshell(os.path.join(STUDENTS_FOLDER, tp_slug, REPO_FOLDER.format(tp_slug=tp_slug, login=login)))
