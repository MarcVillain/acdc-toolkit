import os
import pwd

from helpers.io import folder_ls


def get_arg_number(line, begidx):
    argnum = 0
    start = 0
    while start < len(line) and line[start] == ' ':
        start += 1
    for i in range(start + 1, min(len(line), begidx)):
        if line[i] == ' ' and line[i - 1] != ' ':
            argnum += 1
    return argnum


def get_arg_value(line, number):
    argnum = 0
    start = 0
    while start < len(line) and line[start] == ' ':
        start += 1
    while argnum < number:
        while start < len(line) and line[start] != ' ':
            start += 1
        while start < len(line) and line[start] == ' ':
            start += 1
        argnum += 1
    end = start
    while end < len(line) and line[end] != ' ':
        end += 1
    return line[start:end]


def get_args(line, filter=None):
    if filter is None:
        filter = lambda i, arg: True
    args = []
    start = 0
    number = 0
    while start < len(line) and line[start] == ' ':
        start += 1
    while start < len(line):
        arg_start = start
        while start < len(line) and line[start] != ' ':
            start += 1
        arg = line[arg_start:start]
        if filter(number, arg):
            args.append(arg)
        while start < len(line) and line[start] == ' ':
            start += 1
        number += 1
    return args


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


def remove_duplicates(options, line, current, nb_args):
    used = get_args(line, lambda i, arg: i > nb_args and i != current)
    return [option
            for option in options
            if option not in used]


def autocomplete(text, line, begidx, endidx, arguments, options):
    number = get_arg_number(line, begidx)
    if begidx > 0 and line[begidx - 1] == '=':
        while begidx > 0 and line[begidx - 1] != ' ':
            begidx -= 1
        text = line[begidx:endidx]
    if number <= len(arguments):
        return filter_autocomplete(text, arguments[number - 1])
    else:
        return filter_autocomplete(text, remove_duplicates(options, line, number, len(arguments)))
