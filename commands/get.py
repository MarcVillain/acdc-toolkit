import os

from helpers.autocomplete import autocomplete
from helpers.command import exec_in_folder
from helpers.git import git_clone, git_checkout_tag
from helpers.io import folder_create_if_not_exists, folder_exists, folder_remove, folder_ls
from misc.config import SUBMISSION_TAG
from misc.exceptions import GitException
from misc.printer import print_success, print_info, print_error, print_ask, print_warning
from misc.data import Tp, Submission


def cmd_get(tp_slug, logins):
    """
    Download the students repo corresponding to the given TP slug
    :param tp_slug: Slug of the TP to download
    :param logins: List of student logins
    """
    tp = Tp(tp_slug)
    overwrite = None

    # For each student
    for i, login in enumerate(logins):
        repo = Submission(tp_slug, login)

        print_info(login + ":", percent_pos=i, percent_max=len(logins))

        # If folder exists, delete it
        if repo.exists_locally():
            print_error("Student project already downloaded", 1)
            if overwrite is None:
                ask = print_ask("Do you want to overwrite it?", ['y', 'n', 'ya', 'na'], 1)
                if ask == 'n':
                    print_info("Skipping student project", 1)
                    continue
                if ask == 'na':
                    overwrite = False
                    print_info("Skipping student project", 1)
                    continue
                elif ask == 'ya':
                    overwrite = True
            elif not overwrite:
                print_info("Skipping student project", 1)
                continue

            if overwrite:
                print_info("Overwriting student project", 1)
            folder_remove(repo.local_dir())

        try:
            # Clone the repo
            containing_dir = os.path.abspath(os.path.join(repo.local_dir(), os.pardir))
            folder_create_if_not_exists(containing_dir)
            exec_in_folder(
                tp.local_dir(),
                git_clone, repo.url())
            print_success("Download repository", 1)

            if len(folder_ls(repo.local_dir(), excludes=["\..*"])) == 0:
                print_warning("The repository is empty", 1)
                continue

        except GitException as e:
            print_error("Download: Repository not found", 1)
            continue

        try:
            # Checkout tag submission
            exec_in_folder(
                repo.local_dir(),
                git_checkout_tag, SUBMISSION_TAG
            )
            print_success("Checkout tag " + SUBMISSION_TAG, 1)

        except GitException as e:
            print_error("Checkout: Tag " + SUBMISSION_TAG + " not found", 1)


def cplt_get(text, line, begidx, endidx, options):
    return autocomplete(text, line, begidx, endidx,
                        [[ tp.slug() for tp in Tp.get_local_tps() ]],
                        options)
