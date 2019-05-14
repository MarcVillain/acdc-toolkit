import os
import pwd

from helpers.io import folder_ls


def _progress_in_line(line, i, filter):
    while i < len(line) and filter(line[i]):
        i += 1
    return i


def parse_args(line):
    args = []
    end = 0
    start = _progress_in_line(line, 0, lambda c: c == ' ')
    while start < len(line):
        end = _progress_in_line(line, start, lambda c: c != ' ')
        args.append((line[start:end], start, end))
        start = _progress_in_line(line, end, lambda c: c == ' ')
    return args


def get_arg_number(args, begidx):
    i = 0
    for arg, start, end in args:
        if begidx <= end:
            return i
        i += 1
    return i


def get_arg_value(args, begidx):
    for arg, start, end in args:
        if begidx <= end:
            if start > begidx:
                return ''
            return arg
    return ''


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


def remove_duplicates(options, args, current, nb_args):
    used = [arg
            for i, (arg, start, end) in enumerate(args)
            if i > nb_args and i != current]
    return [option
            for option in options
            if option not in used]


def autocomplete(text, line, begidx, endidx, arguments, options):
    args = parse_args(line)
    number = get_arg_number(args, begidx)
    if begidx > 0 and line[begidx - 1] == '=':
        while begidx > 0 and line[begidx - 1] != ' ':
            begidx -= 1
        text = line[begidx:endidx]
    if number <= len(arguments):
        return filter_autocomplete(text, arguments[number - 1])
    else:
        return filter_autocomplete(text, remove_duplicates(options, args, number, len(arguments)))
