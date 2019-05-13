import os

from helpers.command import exec_in_folder
from helpers.git import git_clone, git_checkout_tag
from helpers.io import folder_create_if_not_exists, folder_exists, folder_remove
from misc.config import REPO_URL, REPO_FOLDER, SUBMISSION_TAG, STUDENTS_FOLDER
from misc.exceptions import GitException
from misc.printer import print_success, print_info, print_error, print_ask


def cmd_get(tp_slug, logins):
    """
    Download the students repo corresponding to the given TP slug
    :param tp_slug: Slug of the TP to download
    :param logins: List of student logins
    """
    tp_folder = os.path.join(STUDENTS_FOLDER, tp_slug)

    if folder_exists(tp_folder):
        print_error("TP " + tp_slug + " already downloaded")
        if not print_ask("Do you want to override it?"):
            return

    folder_create_if_not_exists(tp_folder)

    # For each student
    for i, login in enumerate(logins):
        print_info(login + ":", percent_pos=i, percent_max=len(logins))
        repo_folder = os.path.join(tp_folder, REPO_FOLDER.format(login=login, tp_slug=tp_slug))

        # If folder exists, delete it
        if folder_exists(repo_folder):
            folder_remove(repo_folder)

        try:
            # Clone the repo
            exec_in_folder(
                tp_folder,
                git_clone, REPO_URL.format(login=login, tp_slug=tp_slug)
            )
            print_success("Download repository", 1)

        except GitException as e:
            print_error("Download: Repository not found", 1)
            continue

        try:
            # Checkout tag submission
            exec_in_folder(
                repo_folder,
                git_checkout_tag, SUBMISSION_TAG
            )
            print_success("Checkout tag " + SUBMISSION_TAG, 1)

        except GitException as e:
            print_error("Checkout: Tag " + SUBMISSION_TAG + " not found", 1)
