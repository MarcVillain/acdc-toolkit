import os
import re

from helpers.command import run_command_detached
from misc.config import DEFAULT_LOGINS_FILE


def format_to_regex(string, *args, **kwargs):
    # splitting format string
    parts = []
    in_braces = False
    part_begin = 0
    braces_open = None
    for i in range(len(string)):
        c = string[i]
        if c == '{':
            if braces_open == i - 1:
                braces_open = None
            else:
                braces_open = i
        elif c == '}':
            if braces_open is not None:
                parts.append(string[part_begin:braces_open])
                parts.append(string[braces_open:i+1])
                part_begin = i + 1
                braces_open = None
    if part_begin < len(string):
        parts.append(string[part_begin:])

    # adjusting parts separately
    for i in range(0, len(parts), 2):
        parts[i] = '(?:' + re.escape(parts[i]) + ')'
    for i in range(len(args)):
        args[i] = '(' + args[i] + ')'
    for key in kwargs:
        kwargs[key] = '(?P<' + key + '>' + kwargs[key] + ')'

    # putting everything back together
    return ''.join(parts).format(*args, **kwargs)


def get_logins(file, logins=None):
    if logins is None:
        logins = []

    if len(logins) is 0 and file is None:
        file = DEFAULT_LOGINS_FILE

    if file is not None:
        for login in open(os.path.expanduser(file), "r"):
            if login is "":
                continue
            logins.append(login.strip("\n\r\t "))

    for login in logins:
        if login not in logins:
            logins.append(login)

    return logins
