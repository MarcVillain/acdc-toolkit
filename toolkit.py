#!/usr/bin/env python

import cmd
import os
import sys
import shlex
import traceback

from commands.archive import cmd_archive, cplt_archive
from commands.edit import cmd_edit, cplt_edit
from helpers.other import get_logins

try:
    import readline

    readline.set_completer_delims(' =')
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
            return

        except SystemExit:
            return

        try:
            return func(self, opt)

        except Exception as e:
            if __debug__:
                print_error('An exception occured:')
                traceback.print_exc()
            else:
                print_error(e)

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
        """Usage: get <tp_slug> [<login>...] [--file=<logins_file>]"""
        tp_slug = args["<tp_slug>"]
        logins = get_logins(args["--file"], args["<login>"])
        cmd_get(tp_slug, logins)

    def complete_get(self, text, line, begidx, endidx):
        return cplt_get(text, line, begidx, endidx,
                        [{'name': '--file=', 'file': True}])

    """ remove """

    @docopt_cmd
    def do_remove(self, args):
        """Usage: remove <tp_slug> [<login>...] [--file=<logins_file>] [-a|--all] [-m|--moulinette]"""
        remove_all = args["-a"] or args["--all"]
        remove_moulinette = args["-m"] or args["--moulinette"]
        if remove_all:
            logins = []
        else:
            logins = get_logins(args["--file"], args["<login>"])
        cmd_remove(args['<tp_slug>'], logins, remove_all, remove_moulinette)

    def complete_remove(self, text, line, begidx, endidx):
        return cplt_remove(text, line, begidx, endidx, ['-a', '--all'])

    """ list """

    @docopt_cmd
    def do_list(self, args):
        """Usage: list [<tp_slug>]"""
        cmd_list(args["<tp_slug>"])

    def complete_list(self, text, line, begidx, endidx):
        return cplt_list(text, line, begidx, endidx, [])

    """ edit """

    @docopt_cmd
    def do_edit(self, args):
        """Usage: edit <tp_slug> <login>"""
        cmd_edit(args["<tp_slug>"], args["<login>"])

    def complete_edit(self, text, line, begidx, endidx):
        return cplt_edit(text, line, begidx, endidx, [])

    """ tag """

    @docopt_cmd
    def do_tag(self, args):
        """Usage: tag <tp_slug> <date:yyyy-mm-dd> [<login>...] [--file=<logins_file>] [--name=<tag_name>]"""
        logins = get_logins(args["--file"], args["<login>"])
        cmd_tag(args["<tp_slug>"],
                args["--name"],
                args["<date:yyyy-mm-dd>"],
                logins)

    def complete_tag(self, text, line, begidx, endidx):
        return cplt_tag(text, line, begidx, endidx,
                        ['--name=', {'name': '--file=', 'file': True}])

    """ correct """

    @docopt_cmd
    def do_correct(self, args):
        """Usage: correct <tp_slug> [<login>...] [--file=<logins_file>] [-g|--get] [--no-rider]"""
        logins = get_logins(args["--file"], args["<login>"])
        get_rendus = args["-g"] or args["--get"]
        cmd_correct(args["<tp_slug>"], args["--no-rider"], logins, get_rendus)

    def complete_correct(self, text, line, begidx, endidx):
        return cplt_correct(text, line, begidx, endidx,
                            ['-g', '--get', '--no-rider', {'name': '--file=', 'file': True}])

    """ archive """

    @docopt_cmd
    def do_archive(self, args):
        """Usage: archive <tp_slug> [<login>...] [--file=<logins_file>] [--output=<output_file>] [-v|--verbose]"""
        logins = get_logins(args["--file"], args["<login>"])
        verbose = args["-v"] or args["--verbose"]
        cmd_archive(args["<tp_slug>"], logins, args["--output"], verbose)

    def complete_archive(self, text, line, begidx, endidx):
        return cplt_archive(text, line, begidx, endidx,
                            [{'name': '--file=', 'file': True}])

    """ update """

    @docopt_cmd
    def do_update(self, args):
        """Usage: update"""
        cmd_update()

    """                    """
    """  Default commands  """
    """                    """

    @docopt_cmd
    def do_clear(self, args):
        """Usage: clear"""
        os.system("clear")

    @docopt_cmd
    def do_help(self, args):
        """Usage: help [<command>]"""
        if args["<command>"] and args["<command>"] in FUNC_DOC:
            print(FUNC_DOC[args["<command>"]])
        else:
            print("Commands:")
            for cmd in FUNC_DOC:
                for line in str(FUNC_DOC[cmd]).splitlines():
                    if "Usage: " in line:
                        print("    " + line.replace("Usage: ", ""))

    @docopt_cmd
    def do_exit(self, args):
        """Usage: exit"""
        return True

    def default(self, command):
        if command is "EOF":
            print("exit")
            return True
        if command is "":
            return
        print(str(command).split(" ")[0] + ": command not found")


if __name__ == '__main__':
    if os.path.dirname(sys.argv[0]) != '':
        os.chdir(os.path.dirname(sys.argv[0]))
    dispatcher = CommandDispatcher()
    if len(sys.argv) > 1:
        line = ' '.join(sys.argv[1:])
        line = dispatcher.precmd(line)
        stop = dispatcher.onecmd(line)
    else:
        dispatcher.cmdloop()
