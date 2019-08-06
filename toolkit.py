#!/usr/bin/env python

import cmd
import os
import sys
import shlex
import traceback

from commands.archive import cmd_archive, cplt_archive
from commands.edit import cmd_edit, cplt_edit
from helpers.other import get_logins
from misc.config import EXIT_SUCCESS, EXIT_UNEXPECTED

try:
    import readline

    readline.set_completer_delims(' ')
except ImportError:
    readline = None

from commands.tag import cmd_tag, cplt_tag
from misc.config import HISTORY_FILE, HISTORY_SIZE

from docopt import docopt, DocoptExit

from commands.get import cmd_get, cplt_get
from commands.list import cmd_list, cplt_list
from commands.remove import cmd_remove, cplt_remove
from commands.update import cmd_update
from commands.correct import cmd_correct, cplt_correct
from misc.printer import print_error

# Save the doc of each referenced function to
# simplify the work of the help command
FUNC_DOC = {}


def docopt_cmd(func):
    """
    This decorator is used to register the functions to call
    when a command is sent to the program and avoid having
    to put try/catch everywhere
    """

    def fn(self, arg):
        try:
            opt = docopt(fn.__doc__, shlex.split(arg))

        except DocoptExit as usage:
            print(fn.__doc__)
            self._last_exit_status = EXIT_UNEXPECTED
            return False

        except SystemExit as e:
            self._last_exit_status = e.code
            return True

        try:
            return func(self, opt)

        except Exception as e:
            if __debug__:
                print_error('An exception occured:')
                traceback.print_exc()
            else:
                print_error(e)
            self._last_exit_status = EXIT_UNEXPECTED
            return True

    fn.__name__ = func.__name__
    fn.__doc__ = func.__doc__
    fn.__dict__.update(func.__dict__)
    FUNC_DOC[func.__name__[3:]] = func.__doc__
    return fn


class CommandDispatcher(cmd.Cmd):
    """
    All the commands and their usage are located in this class.
    Here, you can do all the checks you want on the arguments.
    Then you can call the appropriate function to execute the command.
    """
    intro = ("                                B█        ███    ██████     ███\n"
             "         G██████    G██          B███     ██   ██  ██   ██  ██   ██\n"
             "      G█████       G██   ██     B██ ██    ██       ██    █  ██\n"
             "    G█████ R███     G█████      B███████   ██   ██  ██   ██  ██   ██\n"
             "     G███    R███ G████        B██     ██    ███    ██████     ███\n"
             "             G█████\n"
             "            G███ R████        B██████  █████   █████  ██    ██  ██  ██ ██████\n"
             "          G████   R██████       B██   ██   ██ ██   ██ ██    █████   ██   ██\n"
             "        G████        R█████     B██   ██   ██ ██   ██ ██    ██ ███  ██   ██\n"
             "       G███            R███     B██    █████   █████  █████ ██   ██ ██   ██C\n") \
        .replace("G", "\033[37m") \
        .replace("R", "\033[31m") \
        .replace("B", "\033[34m") \
        .replace("C", "\033[0m")

    prompt = "ACDC Toolkit $ "
    file = None

    def __init__(self):
        self._last_exit_status = EXIT_SUCCESS
        super().__init__()

    def last_exit_status(self):
        return self._last_exit_status

    def preloop(self):
        if readline and os.path.exists(HISTORY_FILE):
            readline.read_history_file(HISTORY_FILE)

    def cmdloop(self, intro=None):
        if intro is None:
            print(self.intro)
        else:
            print(intro)
        while True:
            try:
                super(CommandDispatcher, self).cmdloop(intro="")
                break
            except KeyboardInterrupt:
                print("^C")
                self.postloop()

    def postloop(self):
        if readline:
            readline.set_history_length(HISTORY_SIZE)
            readline.write_history_file(HISTORY_FILE)

    """                   """
    """  Custom commands  """
    """                   """

    def completenames(self, text, *ignored):
        completions = super().completenames(text, *ignored)
        if len(completions) == 1:
            return [completions[0] + ' ']
        return completions

    """ get """

    @docopt_cmd
    def do_get(self, args):
        """Usage: get TP_SLUG [LOGIN...] [--file=LOGINS_FILE] [--overwrite|--keep]

Download student submissions for working on them locally.

Arguments:
  TP_SLUG  name of the concerned TP
  LOGIN    login for witch a submission must be downloaded

Options:
  --file=LOGINS_FILE  path to a login list
  -o, --overwrite     if already downloaded, overwrite without asking
  -k, --keep          if already downloaded, skip without asking"""
        tp_slug = args['TP_SLUG']
        logins = get_logins(args['--file'], args['LOGIN'])
        overwrite_policy = None
        if args['--keep']:
            overwrite_policy = False
        elif args['--overwrite']:
            overwrite_policy = True
        self._last_exit_status = cmd_get(tp_slug, logins, overwrite_policy)
        return False

    def complete_get(self, text, line, begidx, endidx):
        return cplt_get(text, line, begidx, endidx)

    """ remove """

    @docopt_cmd
    def do_remove(self, args):
        """Usage: remove TP_SLUG [LOGIN...] [--file=LOGINS_FILE] [--all] [--moulinette]

Remove local copies of student submissions.

Arguments:
  TP_SLUG  name of the concerned TP
  LOGIN    login for witch a submission must be removed

Options:
  --file=LOGINS_FILE  path to a login list
  -a, --all           remove all submissions for this TP
  -m, --moulinette    remove the moulinette along with the submissions"""
        remove_all = args["--all"]
        remove_moulinette = args["--moulinette"]
        if remove_all:
            logins = []
        else:
            logins = get_logins(args["--file"], args["LOGIN"])
        self._last_exit_status = cmd_remove(
            args['TP_SLUG'], logins, remove_all, remove_moulinette)
        return False

    def complete_remove(self, text, line, begidx, endidx):
        return cplt_remove(text, line, begidx, endidx)

    """ list """

    @docopt_cmd
    def do_list(self, args):
        """Usage: list
       list TP_SLUG

In the first form, list all TPs for which submissions are available locally.
In the the second form, list all submissions for a given TP."""
        self._last_exit_status = cmd_list(args["TP_SLUG"])
        return False

    def complete_list(self, text, line, begidx, endidx):
        return cplt_list(text, line, begidx, endidx)

    """ edit """

    @docopt_cmd
    def do_edit(self, args):
        """Usage: edit TP_SLUG LOGIN

Open an interactive shell in the local copy of a student submission.

Arguments:
  TP_SLUG  corresponding TP
  LOGIN    author of the submission"""
        self._last_exit_status = cmd_edit(args["TP_SLUG"], args["LOGIN"])
        return False

    def complete_edit(self, text, line, begidx, endidx):
        return cplt_edit(text, line, begidx, endidx)

    """ tag """

    @docopt_cmd
    def do_tag(self, args):
        """Usage: tag TP_SLUG YYYY-MM-DD [LOGIN...] [--file=LOGINS_FILE] [--name=TAG_NAME]"""
        logins = get_logins(args["--file"], args["LOGIN"])
        self._last_exit_status = cmd_tag(
            args["TP_SLUG"],
            args["YYYY-MM-DD"],
            args["--name"],
            logins)
        return False

    def complete_tag(self, text, line, begidx, endidx):
        return cplt_tag(text, line, begidx, endidx)

    """ correct """

    @docopt_cmd
    def do_correct(self, args):
        """Usage: correct TP_SLUG [LOGIN...] [--file=LOGINS_FILE] [--get] [--no-rider]

Launches an interactive correcting session.

Arguments:
  TP_SLUG  name of the TP being corrected
  LOGIN    students to be corrected

Options:
  --file=LOGINS_FILE path to a login list
  -g, --get          start by downloading the submission
  --no-rider         don't launch the Rider IDE"""
        logins = get_logins(args["--file"], args["LOGIN"])
        get_rendus = args["--get"]
        self._last_exit_status = cmd_correct(
            args["TP_SLUG"], args["--no-rider"], logins, get_rendus)
        return False

    def complete_correct(self, text, line, begidx, endidx):
        return cplt_correct(text, line, begidx, endidx)

    """ archive """

    @docopt_cmd
    def do_archive(self, args):
        """Usage: archive TP_SLUG [LOGIN...] [--file=LOGINS_FILE] [--output=OUTPUT_FILE] [--verbose]

Create an archive containing several submissions.

Arguments:
  TP_SLUG  name of the TP being archived
  LOGIN    students whose submission is to be included in the archive

Options:
  --file=LOGINS_FILE    path to a login list
  --output=OUTPUT_FILE  path to the archive file
  -v, --verbose         enable additional logging"""
        logins = get_logins(args["--file"], args["LOGIN"])
        verbose = args["--verbose"]
        self._last_exit_status = cmd_archive(
            args["TP_SLUG"], logins, args["--output"], verbose)
        return False

    def complete_archive(self, text, line, begidx, endidx):
        return cplt_archive(text, line, begidx, endidx)

    """ update """

    @docopt_cmd
    def do_update(self, args):
        """Usage: update"""
        self._last_exit_status = cmd_update()
        return False

    """                    """
    """  Default commands  """
    """                    """

    @docopt_cmd
    def do_clear(self, args):
        """Usage: clear"""
        os.system("clear")
        self._last_exit_status = EXIT_SUCCESS
        return False

    @docopt_cmd
    def do_help(self, args):
        """Usage: help [COMMAND]"""
        if args["COMMAND"] and args["COMMAND"] in FUNC_DOC:
            print(FUNC_DOC[args["COMMAND"]])
        else:
            print("Commands:")
            for cmd in FUNC_DOC:
                for line in str(FUNC_DOC[cmd]).splitlines():
                    if "Usage: " in line:
                        print("    " + line.replace("Usage: ", ""))
        self._last_exit_status = EXIT_SUCCESS
        return False

    @docopt_cmd
    def do_exit(self, args):
        """Usage: exit"""
        return True

    def default(self, command):
        if command is "EOF":
            self._last_exit_status = EXIT_SUCCESS
            print("exit")
            return True
        if command is not "":
            self._last_exit_status = EXIT_UNEXPECTED
            print(str(command).split(" ")[0] + ": command not found")
        return False


def handle_global_options(argv):
    WD_OPT='--working-directory='
    i = 0
    while i < len(argv):
        if argv[i].startswith(WD_OPT):
            os.chdir(argv[i][len(WD_OPT):])
            del argv[i]
        else:
            i += 1


if __name__ == '__main__':
    handle_global_options(sys.argv)
    dispatcher = CommandDispatcher()
    if len(sys.argv) > 1:
        line = ' '.join(sys.argv[1:])
        dispatcher.onecmd(line)
        sys.exit(dispatcher.last_exit_status())
    else:
        dispatcher.cmdloop()
