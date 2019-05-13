import os

from commands.get import cmd_get
from helpers.command import exec_in_folder
from helpers.git import git_checkout_date, git_tag, git_push_tags
from misc.config import SUBMISSION_TAG, STUDENTS_FOLDER, REPO_FOLDER
from misc.exceptions import GitException
from misc.printer import print_error, print_info, print_success


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
        folder = os.path.join(STUDENTS_FOLDER, tp_slug, REPO_FOLDER.format(tp_slug=tp_slug, login=login))

        try:
            exec_in_folder(folder, git_checkout_date, date, "23:42")
            print_success("Checkout last commit before " + date + " 23:42", 1)
        except GitException as e:
            print_error("Checkout: " + str(e), 1)
            continue

        try:
            exec_in_folder(folder, git_tag, tag_name)
            print_success("Tagging commit", 1)
        except GitException as e:
            print_error("Tagging: " + str(e), 1)
            continue

        try:
            exec_in_folder(folder, git_push_tags)
            print_success("Tagging commit", 1)
        except GitException as e:
            print_error("Tagging: " + str(e), 1)
            continue