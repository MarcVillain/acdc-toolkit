import os

from helpers.io import folder_exists, folder_ls
from misc.config import STUDENTS_FOLDER


def get_downloaded_students(tp_slug):
    student_folder = os.path.join(STUDENTS_FOLDER, tp_slug)
    if not folder_exists(student_folder):
        return []
    return [folder[len(tp_slug) + 1:]
            for folder in folder_ls(student_folder)
            if folder.startswith(tp_slug + "-")]
