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
    rev_list = run_command('git rev-list -n 1 --before="' + date + ' ' + hour + '" master')
    if rev_list.returncode is not 0:
        raise GitException("Cannot find last commit before " + date + " 23:42")
    git_checkout_tag(rev_list.stdout)


def git_checkout_tag(tag):
    run_command("git stash")
    res = run_command("git checkout " + tag)
    if res.returncode is not 0:
        raise GitException("Cannot checkout " + tag)


def git_clone(repo, dest, tag=None):
    if os.path.exists(dest):
        raise IOError('Cannot clone, path already exists.')

    # If required, creating parent directory
    containing_dir=parent_dir(dest)
    existing_dir=containing_dir
    created_dir=None
    while not os.path.isdir(existing_dir):
        created_dir = existing_dir
        existing_dir = parent_dir(existing_dir)
    if created_dir is not None:
        os.makedirs(created_dir)

    # Running git
    try:
        cmd = 'git clone '+repo+' '+dest
        if tag is not None:
            cmd += ' --branch='+tag
        if run_command(cmd).returncode is not 0:
            raise GitException("Cannot clone " + repo)
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
