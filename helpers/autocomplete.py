import os
import pwd
import re
import datetime

from helpers.io import folder_ls
from helpers.other import get_logins
from misc.data import Tp, Submission


def filter_proposals(proposals, text, prefer_prefix=True):
    valid_set = set()
    for entry in proposals:
        if prefer_prefix:
            is_valid = (entry[:len(text)] == text)
        else:
            is_valid = (text in entry)
        if is_valid:
            valid_set.add(entry)
    if prefer_prefix and len(valid_set) == 0:
        return filter_proposals(proposals, text, False)
    return list(valid_set)


def enum_nothing(text, line):
    return []


def enum_dates(text, line):
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    if now[:len(text)] == text:
        return [ now+' ' ]
    else:
        return []


def enum_logins(text, line):
    try:
        return [ login+' '
                 for login in filter_proposals(get_logins(None), text) ]
    except:
        return []


def enum_tp_slugs(text, line):
    return filter_proposals(
        [ tp.slug()+' ' for tp in Tp.get_local_tps() ],
        text)


def enum_logins_for_tp(text, line):
    logins = []
    for arg in line.replace('=', ' ').split(' ')[1:]:
        if len(arg) != 0 and arg[0] != '-':
            tp = Tp(arg)
            if tp.has_local_submissions():
                logins += [ sub.login()+' '
                            for sub in tp.get_local_submissions() ]
    return filter_proposals(logins, text)


def enum_files(text, line):
    if len(text) == 0:
        text = os.path.curdir
    else:
        text = os.path.expanduser(text)
    parent = os.path.abspath(os.path.join(text, os.path.pardir))
    if text[-1] == os.path.sep:
        if os.path.isdir(text):
            parent = text
            entries = folder_ls(parent, excludes=['\\..*'])
        elif os.path.exists(text[:-1]):
            return [ text[:-1]+' ' ]
        else:
            return []
    elif os.path.isdir(text):
        return [ os.path.join(text, '') ]
    elif os.path.isdir(parent):
        basename = os.path.basename(text)
        entries = folder_ls(
            parent,
            includes=['.*'+re.escape(basename)+'.*'],
            excludes=[] if basename[0] == '.' else ['\\..*'])
        entries = filter_proposals(entries, basename)
    else:
        return []
    for i in range(len(entries)):
        entry = os.path.join(parent, entries[i])
        entry += os.path.sep if os.path.isdir(entry) else ' '
        entries[i] = entry
    return entries


class CmdCompletor:
    def __init__(self, options, opts_enum_funcs, positional_enum_funcs):
        self._options = options + list(opts_enum_funcs.keys())
        self._opts_enum_funcs = opts_enum_funcs
        self._positional_enum_funcs = positional_enum_funcs


    def _get_position(self, line, index):
        position = -1
        in_option = False
        in_word = False
        for c in line[:index]:
            now_in_word = c != ' '
            if in_word and not now_in_word and not in_option:
                position += 1
            if not in_word and c == '-':
                in_option = True
            if not now_in_word:
                in_option = False
            in_word = now_in_word
        return position


    def _complete_option_value(self, text, line):
        sep = text.find('=') + 1
        option = text[:sep]
        value = text[sep:]
        if not (option in self._opts_enum_funcs):
            return []
        entries = self._opts_enum_funcs[option](value, line)
        return [ option+entry for entry in entries ]


    def _complete_positional(self, text, line, position):
        if position < len(self._positional_enum_funcs):
            return self._positional_enum_funcs[position](text, line)
        else:
            return self._positional_enum_funcs[-1](text, line)


    def _complete_long_option(self, text):
        return [ (op if op[-1] == '=' else op+' ')
                 for op in self._options
                 if op[:len(text)] == text ]


    def _suggest_short_options(self, text):
        return [ text+op[1]+' '
                 for op in self._options
                 if (len(op) == 2 and not op[1] in text) ]


    def _suggest_options(self):
        return [ (op if op[-1] == '=' else op+' ')
                 for op in self._options ]


    def _suggest_any(self, line, position):
        return self._suggest_options() \
            + self._complete_positional('', line, position)


    def complete(self, text, line, begidx, endidx):
        assert len(line) != 0
        if len(text) == 0:
            return self._suggest_any(line, self._get_position(line, begidx))
        elif re.search('^--[a-zA-Z0-9_-]+=', text) is not None:
            return self._complete_option_value(text, line)
        elif text[0] == '-':
            if len(text) == 1:
                return self._suggest_options()
            elif text[1] == '-':
                return self._complete_long_option(text)
            else:
                return self._suggest_short_options(text)
        else:
            return self._complete_positional(
                text, line, self._get_position(line, begidx))
