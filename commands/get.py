import os

from helpers.autocomplete import CmdCompletor, enum_tp_slugs, enum_logins, enum_files
from helpers.command import exec_in_folder
from helpers.git import git_clone, git_checkout_tag
from helpers.io import folder_create_if_not_exists, folder_exists, folder_remove, folder_ls
from misc.config import SUBMISSION_TAG, EXIT_SUCCESS, EXIT_FAILURE
from misc.exceptions import GitException
from misc.printer import print_success, print_info, print_error, print_ask, print_warning
from misc.data import Tp, Submission


def cmd_get(tp_slug, logins, overwrite_policy):
    """
    Download the students repo corresponding to the given TP slug
    :param tp_slug: Slug of the TP to download
    :param logins: List of student logins
    """
    tp = Tp(tp_slug)
    success = True

    # For each student
    for i, login in enumerate(logins):
        repo = Submission(tp_slug, login)

        print_info(login + ":", percent_pos=i, percent_max=len(logins))

        # If folder exists, delete it
        if repo.exists_locally():
            overwrite = overwrite_policy
            if overwrite is None:
                print_error("Student project already downloaded", 1)
                ask = print_ask("Do you want to overwrite it?", ['y', 'n', 'ya', 'na'], 1)
                overwrite = ask in [ 'y', 'ya' ]

            if overwrite:
                print_info("Overwriting student project", 1)
            else:
                print_info("Skipping student project", 1)
                continue

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
            success = False
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
            success = False

    return EXIT_SUCCESS if success else EXIT_FAILURE


CPLT = CmdCompletor(
    [ '-o', '--overwrite', '-k', '--keep' ],
    { '--files=': enum_files },
    [ enum_tp_slugs, enum_logins ])

def cplt_get(text, line, begidx, endidx):
    return CPLT.complete(text, line, begidx, endidx)
