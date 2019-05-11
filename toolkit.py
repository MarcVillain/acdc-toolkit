#!/usr/bin/env python

import cmd
import os
import sys
import readline
readline.set_completer_delims(' =')

from docopt import docopt, DocoptExit

from commands.get import cmd_get
from commands.list import cmd_list
from commands.remove import cmd_remove
from commands.update import cmd_update
from commands.correct import cmd_correct, cplt_correct
from misc.helpers import get_logins
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
            opt = docopt(fn.__doc__, arg)

        except DocoptExit as usage:
            print(fn.__doc__)
            return

        except SystemExit:
            return

        try:
            return func(self, opt)

        except Exception as e:
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

    """                   """
    """  Custom commands  """
    """                   """

    def completenames(self, text, *ignored):
        completions = super().completenames(text, *ignored)
        if len(completions) == 1:
            return [completions[0] + ' ']
        return completions


    @docopt_cmd
    def do_get(self, args):
        """Usage: get <tp_slug> [<login>...] [--file=<logins_file>]"""
        tp_slug = args["<tp_slug>"]
        logins = get_logins(args["--file"], args["<login>"])
        cmd_get(tp_slug, logins)

    @docopt_cmd
    def do_remove(self, args):
        """Usage: remove <tp_slug>"""
        cmd_remove(args['<tp_slug>'])

    @docopt_cmd
    def do_list(self, args):
        """Usage: list [-d]"""
        cmd_list(args["-d"])

    @docopt_cmd
    def do_correct(self, args):
        """Usage: correct <tp_slug> [--no-rider] [--file=<logins_file>]"""
        logins_file = args["--file"]
        logins = get_logins(logins_file)
        cmd_correct(args["<tp_slug>"], args["--no-rider"], logins)

    def complete_correct(self, text, line, begidx, endidx):
        return cplt_correct(text, line, begidx, endidx,
                            ['--no-rider', {'name': '--file=', 'file': True}])

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
        exit()

    def default(self, command):
        if command is "EOF":
            print()
            exit()
        if command is "":
            return
        print(str(command).split(" ")[0] + ": command not found")


if __name__ == '__main__':
    if os.path.dirname(sys.argv[0]) != '':
        os.chdir(os.path.dirname(sys.argv[0]))
    CommandDispatcher().cmdloop()
