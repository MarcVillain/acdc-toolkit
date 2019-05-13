import errno
import fileinput
import os
import shlex
import shutil
import subprocess
import pwd
import re

from misc.config import DEFAULT_LOGINS_FILE
from misc.exceptions import GitException


def run_command(cmd):
    """
    Execute a shell command
    :param cmd: The command to run
    :return: The return value of the subprocess
    """
    res = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res.stdout = res.stdout.decode('utf-8')[:-1]
    res.stderr = res.stderr.decode('utf-8')[:-1]
    return res


def run_shell_command(cmd):
    return subprocess.call(cmd, shell=True)


def run_command_detached(cmd):
    devnull = open(os.devnull)
    subprocess.Popen(shlex.split(cmd), stdout=devnull, stderr=devnull)


def run_commands(cmds, cmds_fail=None, cmds_finally=None):
    """
    Execute multiple shell commands
    :param cmds: The list of commands to execute
    :param cmds_fail: The commands to execute on fail
    :param cmds_finally: The commands to execute at the end whatever happens
    :return: The return value of the last command of 'cmds'
    """
    if cmds_finally is None:
        cmds_finally = []
    if cmds_fail is None:
        cmds_fail = []
    ret_val = None

    # Run every command
    for cmd in cmds:
        ret_val = run_command(cmd)
        # Run fail commands on fail
        if ret_val.returncode is not 0:
            for cmd_fail in cmds_fail:
                run_command(cmd_fail)
            break

    # Run finally commands
    for cmd_finally in cmds_finally:
        run_command(cmd_finally)

    return ret_val


def get_logins(file, logins=None):
    if logins is None:
        logins = []

    if len(logins) is 0 and file is None:
        file = DEFAULT_LOGINS_FILE

    if file is not None:
        for login in open(file, "r"):
            if login is "":
                continue
            logins.append(login.strip("\n\r\t "))

    for login in logins:
        if login not in logins:
            logins.append(login)

    return logins


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


def folder_ls(folder_path, includes=None, excludes=None):
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


def exec_in_folder(folder_path, func, *func_args):
    dir_backup = os.getcwd()
    os.chdir(folder_path)
    res = 1
    try:
        res = func(*func_args)
    except Exception as e:
        os.chdir(dir_backup)
        raise e

    os.chdir(dir_backup)
    return res


def git_update():
    run_command("git stash")
    res = run_command("git pull")
    if res.returncode is not 0:
        raise GitException("Cannot pull from " + os.getcwd())


def git_checkout_date(date, hour):
    rev_list = run_command('git rev-list -n 1 --before="' + date + ' ' + hour + '" master')
    if rev_list.returncode is not 0:
        raise GitException("Cannot find last commit before " + date + " 23:42")
    git_checkout_tag(rev_list.stdout)


def git_checkout_tag(tag):
    run_command("git stash")
    res = run_command("git checkout " + tag)
    if res.returncode is not 0:
        raise GitException("Cannot checkout " + tag)


def git_clone(repo):
    if run_command('git clone ' + repo).returncode is not 0:
        raise GitException("Cannot clone " + repo)


def git_tag(name):
    if run_command('git tag ' + name).returncode is not 0:
        raise GitException("Cannot add tag " + name)


def git_push_tags():
    if run_command('git push --tags').returncode is not 0:
        raise GitException("Cannot push tags")


def get_arg_number(line, begidx):
    argnum = 0
    start = 0
    while start < len(line) and line[start] == ' ':
        start += 1
    for i in range(start + 1, min(len(line), begidx)):
        if line[i] == ' ' and line[i - 1] != ' ':
            argnum += 1
    return argnum


def validate(text, arg):
    if isinstance(arg, dict):
        return arg['name'].startswith(text)
    else:
        return arg.startswith(text)


def sanitize(args):
    return [arg['name'] if isinstance(arg, dict) else arg for arg in args]


def find_matches(text, arguments):
    return [arg
            for arg in arguments
            if validate(text, arg)]


def autocomplete_path(text, name):
    value = text[len(name):]
    sep = value.rfind(os.path.sep)
    # If there is no / in the path
    if sep == -1:
        if len(value) > 0 and value[0] == '~':
            value = value[1:]
            users = sorted([u[0] for u in pwd.getpwall()])
            return ['~' + u
                    for u in users
                    if u.startswith(value)]
        dir = '.'
        dir_join = ''
        file = value
    # If the only / is at the start
    elif sep == 0:
        dir = os.path.sep
        dir_join = os.path.sep
        file = value[sep + 1:]
    # Otherwise
    else:
        dir = value[:sep]
        dir_join = dir + os.path.sep
        file = value[sep + 1:]
    return [dir_join + f
            for f in folder_ls(os.path.expanduser(dir))
            if f.startswith(file)]


def add_trailing(matches, isFile=False):
    matches = sanitize(matches)
    if len(matches) != 1:
        return matches
    elif not isFile:
        return [matches[0] + ' ']
    elif os.path.isdir(os.path.expanduser(matches[0])):
        return [matches[0] + os.path.sep]
    else:
        return [matches[0] + ' ']


def filter_autocomplete(text, arguments):
    # Find all matches matching starting with text
    matches = find_matches(text, arguments)
    if len(matches) > 1:
        # If there is more than one match, return the matches
        return sanitize(matches)
    elif len(matches) == 1:
        # If there is only one match,
        # but it is equal to the text and ends with =,
        # try to match with value value
        match = matches[0]
        if not isinstance(match, dict):
            if match[-1] == '=':
                return sanitize(matches)
            else:
                return add_trailing(matches)
        if match['name'] != text:
            return sanitize(matches)
        name = match['name']
        if name[-1] != '=':
            return add_trailing(matches)
    else:
        # If there is no match,
        # split text with equals sign,
        # and start again
        matches = find_matches(text.partition('=')[0], arguments)
        if len(matches) != 1:
            return []
        match = matches[0]
        if not isinstance(match, dict):
            return []
        name = match['name']
        if name[-1] != '=':
            return []
    # If we should match a file after the equals sign
    if 'file' in match and match['file']:
        return add_trailing(autocomplete_path(text, name), True)
    return []


def autocomplete(text, line, begidx, endidx, arguments, options):
    number = get_arg_number(line, begidx)
    if begidx > 0 and line[begidx - 1] == '=':
        while begidx > 0 and line[begidx - 1] != ' ':
            begidx -= 1
        text = line[begidx:endidx]
    if number <= len(arguments):
        return filter_autocomplete(text, arguments[number - 1])
    else:
        return filter_autocomplete(text, options)


def open_rider(folder):
    run_command_detached("rider " + folder)
