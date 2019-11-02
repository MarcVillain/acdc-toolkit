import os
import shutil

from helpers.command import run_command
from helpers.io import parent_dir
from misc.exceptions import GitException


def git_update():
    run_command("git stash")
    res = run_command("git pull")
    if res.returncode is not 0:
        raise GitException("Cannot pull from " + os.getcwd())


def git_checkout_date(date, hour):
    rev_list = run_command('git rev-list -n 1 --before="' + str(date) + ' ' + str(hour) + '" master')
    if rev_list.returncode is not 0:
        raise GitException("Cannot find last commit before " + str(date) + " " + hour)
    git_checkout_tag(rev_list.stdout)


def git_checkout_tag(tag):
    run_command("git stash")
    res = run_command("git checkout " + str(tag))
    if res.returncode is not 0:
        raise GitException("Cannot checkout " + str(tag))


def git_clone(repo, dest, tag=None, commit=None):
    assert(tag is None or commit is None)

    if os.path.exists(dest):
        raise IOError('Cannot clone, path already exists.')

    # If required, creating parent directory
    containing_dir = parent_dir(dest)
    existing_dir = containing_dir
    created_dir = None
    while not os.path.isdir(existing_dir):
        created_dir = existing_dir
        existing_dir = parent_dir(existing_dir)
    if created_dir is not None:
        os.makedirs(created_dir)

    # Running git
    try:
        options = ''
        if tag is not None:
            options += f' --branch={tag}'
        cmd = f'git clone{options} {repo} {dest}'
        if run_command(cmd).returncode != 0:
            raise GitException("Cannot clone " + repo)
        if commit is not None:
            r = run_command(f'git -C {dest} checkout {commit}')
            if r.returncode != 0:
                raise GitException(f'Could not checkout {commit}.')
    except:
        if created_dir is not None:
            shutil.rmtree(created_dir)
        raise


def git_tag(name):
    if run_command('git tag ' + name).returncode is not 0:
        raise GitException("Cannot add tag " + name)


def git_push_tags():
    if run_command('git push --tags').returncode is not 0:
        raise GitException("Cannot push tags")
