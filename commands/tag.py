import os

from commands.get import cmd_get
from helpers.autocomplete import CmdCompletor, enum_files, enum_nothing, enum_dates, enum_tp_slugs, enum_logins_for_tp
from helpers.command import exec_in_folder
from helpers.git import git_checkout_date, git_tag, git_push_tags
from helpers.io import folder_ls
from misc.config import SUBMISSION_TAG, EXIT_SUCCESS, EXIT_FAILURE
from misc.exceptions import GitException
from misc.printer import print_error, print_info, print_success
from misc.data import Tp, Submission


def cmd_tag(tp_slug, tag_name, date, logins):
    """
    Push a tag to the last commit of the students before 23h42 at the given date
    :param tp_slug: Slug of the TP
    :param tag_name: Tag name
    :param date: Date in yyyy-mm-dd format
    :param logins: List of student logins
    """
    if tag_name is None:
        tag_name = SUBMISSION_TAG

    cmd_get(tp_slug, logins)

    for i, login in enumerate(logins):
        print_info(login + ":", percent_pos=i, percent_max=len(logins))
        folder = Submission(tp_slug, login).local_dir()
        success = True

        try:
            exec_in_folder(folder, git_checkout_date, date, "23:42")
            print_success("Checkout last commit before " + date + " 23:42", 1)
        except GitException as e:
            print_error("Checkout: " + str(e), 1)
            success = False
            continue

        try:
            exec_in_folder(folder, git_tag, tag_name)
            print_success("Tagging commit", 1)
        except GitException as e:
            print_error("Tagging: " + str(e), 1)
            success = False
            continue

        try:
            exec_in_folder(folder, git_push_tags)
            print_success("Tagging commit", 1)
        except GitException as e:
            print_error("Tagging: " + str(e), 1)
            success = False
            continue

        return EXIT_SUCCESS if success else EXIT_FAILURE


CPLT = CmdCompletor(
    [],
    { '--file=': enum_files, '--name=': enum_nothing },
    [ enum_tp_slugs, enum_dates, enum_logins_for_tp ])

def cplt_tag(text, line, begidx, endidx):
    return CPLT.complete(text, line, begidx, endidx)
