import errno
import fileinput
import os
import re
import shutil


def folder_exists(folder_path):
    return os.path.isdir(folder_path)


def folder_create(folder_path):
    try:
        os.makedirs(folder_path)
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise


def folder_create_if_not_exists(folder_path):
    if not folder_exists(folder_path):
        folder_create(folder_path)


def folder_remove(folder_path):
    shutil.rmtree(folder_path)


def folder_move(folder_path_src, folder_path_dest):
    shutil.move(folder_path_src, folder_path_dest)


def file_matches(file, patterns):
    for pattern in patterns:
        if re.match('^' + pattern + '$', file, re.IGNORECASE):
            return True
    return False


def file_replace(file_path, text_to_search, replacement_text):
    with fileinput.FileInput(file_path, inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace(text_to_search, replacement_text), end='')


def folder_ls(folder_path=".", includes=None, excludes=None):
    if includes is None:
        includes = ['.*']
    if excludes is None:
        excludes = []
    return [file
            for file in os.listdir(folder_path)
            if file_matches(file, includes) and not file_matches(file, excludes)]


def _folder_find(folder_path, folders, includes, excludes, list_dir, depth):
    if depth == 0:
        folders.append(folder_path)
        return
    if depth > 0:
        depth -= 1

    if not os.path.exists(folder_path):
        return

    for file in os.listdir(folder_path):
        path = os.path.join(folder_path, file)
        if file_matches(file, excludes):
            pass
        elif os.path.isdir(path):
            _folder_find(path, folders, includes, excludes, list_dir, depth)
        elif file_matches(file, includes):
            folders.append(path)


def folder_find(folder_path, includes=None, excludes=None, list_dir=False, depth=-1):
    if includes is None:
        includes = ['.*']
    if excludes is None:
        excludes = []
    folders = []
    _folder_find(folder_path, folders, includes, excludes, list_dir, depth)
    return folders


def files_remove(files_paths):
    for file_path in files_paths:
        os.unlink(file_path)


def file_copy(src, dest):
    shutil.copyfile(src, dest)


def file_insert_text_every_n_lines(file_path, text, n):
    f = open(file_path, "r")
    contents = f.readlines()
    f.close()

    i = 0
    while i < len(contents):
        for line in text.split("\n"):
            contents.insert(i, line + "\n")
            i += 1
        i += n

    f = open(file_path, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()
