import datetime
import os
import zipfile

from helpers.autocomplete import autocomplete, get_arg_number, get_arg_value, parse_args
from helpers.command import exec_in_folder
from helpers.io import folder_ls, folder_find, folder_create_if_not_exists
from helpers.terminal import open_subshell
from misc.config import REPO_FOLDER, ACDC_LOCAL_FOLDER
from misc.printer import print_info, print_success
from misc.data import Tp, Submission


def get_all_non_trash_files(student_folder):
    files_to_zip = []
    for file in folder_find(student_folder, excludes=["\\..*", "bin", "obj", "packages"]):
        files_to_zip.append(file)
    return files_to_zip


def archive_current_folder(students_folder, zip_file, verbose):
    files_to_zip = []

    # Compute all files to archive
    for i, student_folder in enumerate(students_folder):
        if not verbose:
            print_info("Adding: " + student_folder, percent_pos=i, percent_max=len(students_folder))
        files_to_zip += get_all_non_trash_files(student_folder)

    # Archive all files
    for i, file_to_zip in enumerate(files_to_zip):
        if verbose:
            print_info("Adding: " + file_to_zip, percent_pos=i, percent_max=len(files_to_zip))
        zip_file.write(file_to_zip, compress_type=zipfile.ZIP_DEFLATED)


def get_students_folder(tp_slug, logins):
    students_folder = []
    if len(logins) == 0:
        students_folder = folder_ls()
    else:
        students_folder = [REPO_FOLDER.format(tp_slug=tp_slug, login=login) for login in logins]
    return students_folder


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

    students_folders_path = Tp(tp_slug).local_dir()

    students_folder = exec_in_folder(students_folders_path,
                                     get_students_folder, tp_slug, logins)

    exec_in_folder(students_folders_path,
                   archive_current_folder, students_folder, zip_file, verbose)

    print_success("Archive successfully created (" + output_file + ")")


def cplt_archive(text, line, begidx, endidx, options):
    args = parse_args(line)
    number = get_arg_number(args, begidx)
    arguments = [[ tp.slug() for tp in Tp.get_local_tps() ]]
    if number > 1:
        arguments.append([ sub.login()
                           for sub in Tp(args[1][0]).get_local_submissions() ])
    return autocomplete(text, line, begidx, endidx,
                        arguments, options)
