import os

from helpers.command import run_command
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


def git_clone(repo):
    if run_command('git clone ' + repo).returncode is not 0:
        raise GitException("Cannot clone " + repo)


def git_tag(name):
    if run_command('git tag ' + name).returncode is not 0:
        raise GitException("Cannot add tag " + name)


def git_push_tags():
    if run_command('git push --tags').returncode is not 0:
        raise GitException("Cannot push tags")
