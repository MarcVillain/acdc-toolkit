import datetime
import os
import zipfile

from helpers.autocomplete import CmdCompletor, enum_files, enum_tp_slugs, enum_logins_for_tp
from helpers.command import exec_in_folder
from helpers.io import folder_ls, folder_find, folder_create_if_not_exists, parent_dir
from helpers.terminal import open_subshell
from misc.config import REPO_FOLDER, ACDC_LOCAL_FOLDER, EXIT_SUCCESS, EXIT_FAILURE
from misc.printer import print_info, print_success, print_error
from misc.data import Tp, Submission


def get_all_non_trash_files(student_folder):
    files_to_zip = [ student_folder ]
    for file in folder_find(student_folder, excludes=["\\..*", "bin", "obj", "packages"]):
        files_to_zip.append(file)
    return files_to_zip


def archive_all(submissions, zip_file, verbose):
    files_to_zip = {}

    # Compute all files to archive
    for i, submission in enumerate(submissions):
        containing_dir = parent_dir(submission.local_dir())
        if not verbose:
            print_info("Adding: " + submission.name(), percent_pos=i, percent_max=len(submissions))
        for path in get_all_non_trash_files(submission.local_dir()):
            files_to_zip[os.path.relpath(path, containing_dir)] = path

    # Archive all files
    for i, arcname in enumerate(files_to_zip):
        if verbose:
            print_info("Adding: " + file_to_zip, percent_pos=i, percent_max=len(files_to_zip))
        zip_file.write(
            files_to_zip[arcname],
            arcname=arcname,
            compress_type=zipfile.ZIP_DEFLATED)


def cmd_archive(tp_slug, logins, output_file, verbose):
    """
    Create an archive with all the students files (without trash files)
    :param tp_slug: TP slug
    :param logins: Students login
    :param output_file: Output file path
    :param verbose: Display more info
    """
    tp = Tp(tp_slug)

    if output_file:
        output_file = os.path.expanduser(output_file)
    else:
        today = datetime.datetime.today()
        archives_folder = os.path.join(ACDC_LOCAL_FOLDER, "archives")
        folder_create_if_not_exists(archives_folder)
        output_file = os.path.join(archives_folder, f"{tp_slug}_{today:%d-%m-%Y_%Hh%M}.zip")

    zip_file = zipfile.ZipFile(output_file, "w")

    if not tp.has_local_submissions():
        return EXIT_FAILURE

    if len(logins) == 0:
        submissions = tp.get_local_submissions()
    else:
        submissions = []
        for login in logins:
                submission = Submission(tp, login)
                if submission.exists_locally():
                        submissions.append(submission)
                else:
                        print_error("Missing submission for {}.".format(login))

    archive_all(submissions, zip_file, verbose)

    print_success("Archive successfully created (" + output_file + ")")
    return EXIT_SUCCESS


CPLT = CmdCompletor(
    [ '-v', '--verbose' ],
    { '--file=': enum_files, '--output=': enum_files },
    [ enum_tp_slugs, enum_logins_for_tp ])

def cplt_archive(text, line, begidx, endidx):
    return CPLT.complete(text, line, begidx, endidx)
