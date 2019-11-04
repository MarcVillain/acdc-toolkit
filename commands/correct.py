import os
import cmd
import shlex
from xml.etree import cElementTree

from commands.correct_actions.all_public import AllPublic
from commands.correct_actions.build import Build
from commands.correct_actions.clear_files import ClearFiles
from commands.correct_actions.exit import Exit
from commands.correct_actions.log import Log
from commands.correct_actions.next import Next
from commands.correct_actions.previous import Previous
from commands.correct_actions.copy_files import CopyFiles
from commands.correct_actions.readme import Readme
from commands.correct_actions.refresh import Refresh
from commands.correct_actions.shell import Shell
from commands.correct_actions.tree import Tree
from commands.get import cmd_get
from getkey import platform, keys

from helpers.autocomplete import CmdCompletor, enum_files, enum_tp_slugs, enum_logins, enum_logins_for_tp
from helpers.command import exec_in_folder, run_shell_command
from helpers.git import git_clone
from helpers.io import folder_ls, folder_find, folder_exists, folder_create, parent_dir
from misc.config import STUDENTS_FOLDER, MOULINETTE_FOLDER, REPO_FOLDER, EXIT_SUCCESS, HISTORY_FILE, CORRECTION_HISTORY_FILE, HISTORY_SIZE
from misc.printer import print_info, print_error, print_success, print_current_exception
from misc.data import Tp, Submission
from misc.moulinettes import DownloadPolicy, CorrectingSession
from helpers.autocomplete import CmdCompletor, filter_proposals, enum_logins_for_tp
from helpers.readline_history import readline_history


class _BadUsageException(Exception):
    pass


class CorrectingSessionSet:
    def __init__(self, moulinette):
        self.__moulinette = moulinette
        self.__sessions = []
        self.__current_index = 0


    def list(self):
        return self.__sessions


    def current(self):
        if len(self.__sessions) == 0:
            return None
        else:
            return self.__sessions[self.__current_index]


    def select(self, sel):
        """@sel can be either a login or an offset"""
        if isinstance(sel, int):
            self.__current_index = \
                (self.__current_index + sel) % len(self.__sessions)
        else:
            tries = 0
            while tries < len(self.__sessions) \
                  and self.current().submission().login() != sel:
                tries += 1
                self.select(+1)


    def restore_current(self):
        submission = self.current().submission()
        self.current().remove()
        self.__sessions[self.__current_index] = \
            self.__moulinette.new_correcting_session(submission)


    def close_current(self):
        self.__sessions.pop(self.__current_index)
        if self.__current_index >= len(self.__sessions):
            self.__current_index = 0


    def open(self, login, assert_not_open=False):
        submission = Submission(self.__moulinette.tp(), login)
        if not assert_not_open:
            for session in self.__sessions:
                if session.submission() == submission:
                    return
        session = self.__moulinette.new_correcting_session(submission)
        self.__sessions.append(session)


    def close(self, login):
        submission = Submission(self.__moulinette.tp(), login)
        if self.current().submission() == submission:
            return self.close_current()
        index = None
        for i in range(len(self.__sessions)):
            if self.__sessions[i].submission() == submission:
                index = i
                break
        if index is not None:
            assert index != self.__current_index
            if index < self.__current_index:
                self.__current_index -= 1


    def print_summary(self):
        print_info('{0} correcting session(s) opened for TP "{1}"'.format(
            len(self.__sessions),
            self.__moulinette.tp().slug()))
        for session in self.__sessions:
            print_info(session.submission().login(), end=': ')
            session.problems().print_one_liner()


    def get_logins(self):
        return [ session.submission().login() for session in self.__sessions ]


def __parse_tests(xml, out):
    for test in xml.findall('test-case'):
        result = test.get('result').lower()
        out['tests'].append({
            'name': test.get('fullname'),
            'result': result,
            'duration': round(float(test.get('duration')) * 1000, 3),
            'asserts': test.get('asserts')
        })
        out['stats']['total'] += 1
        if result in out['stats']:
            out['stats'][result] += 1
        else:
            out['stats'][result] = 1
    for test in xml.findall('test-suite'):
        __parse_tests(test, out)


def parse_tests(path):
    root = cElementTree.parse(path).getroot()
    out = {}
    out['stats'] = {}
    out['stats']['passed'] = 0
    out['stats']['failed'] = 0
    out['stats']['total'] = 0
    out['tests'] = []
    __parse_tests(root, out)
    return out


def _cmd(f):
    def decorated_f(self, args):
        try:
            return f(self, shlex.split(args))
        except _BadUsageException:
            print_error('Bad usage of command.')
            print(decorated_f.__doc__)
        except Exception:
            print_current_exception()
            return False

    decorated_f.__name__ = f.__name__
    decorated_f.__doc__ = f.__doc__
    decorated_f.__dict__.update(f.__dict__)
    return decorated_f


class CommandDispatcher(cmd.Cmd):
    CPLT_OPEN = CmdCompletor(
        [],
        {},
        [ enum_logins ])


    def __init__(self, sessions):
        self.__sessions = sessions
        self.__opened_logins_cplt = CmdCompletor(
            [],
            {},
            [lambda text, line: self.__enum_opened_logins(text, line)])
        super().__init__()


    def __enum_opened_logins(self, text, line):
        logins = self.__sessions.get_logins()
        return [login+' ' for login in filter_proposals(logins, text)]


    def __update_prompt(self):
        submission = self.__sessions.current().submission()
        self.prompt = 'ACDC Correcting {0}/{1} $ '.format(
            submission.tp().slug(), submission.login())


    def __get_enum_logins_func(self):
        def f(text, line):
            logins = [
                session.submission().login()
                for session in self.__sessions ]
            return filter_proposals(logins, text)
        return f


    def preloop(self):
        super().preloop()
        self.__update_prompt()


    def postcmd(self, stop, line):
        if self.__sessions.current() is not None:
            self.__update_prompt()
        return super().postcmd(stop, line)


    def postloop(self):
        super().postloop()
        readline_history.save()


    @_cmd
    def do_next(self, args):
        """Usage: next

Select the next submission."""
        if len(args) != 0:
            raise _BadUsageException()
        self.__sessions.select(+1)
        return False


    @_cmd
    def do_prev(self, args):
        """Usage: next

Select the previous submission."""
        if len(args) != 0:
            raise _BadUsageException()
        self.__sessions.select(-1)
        return False


    @_cmd
    def do_select(self, args):
        """Usage: select LOGIN

Switch to an already opened submission."""
        if len(args) != 1:
            raise _BadUsageException()
        self.__sessions.select(args[0])
        return False


    def complete_select(self, text, line, begidx, endidx):
        return self.__opened_logins_cplt.complete(text, line, begidx, endidx);


    @_cmd
    def do_open(self, args):
        """Usage: open LOGIN...

Open a session for each LOGIN."""
        if len(args) == 0:
            raise _BadUsageException()
        for login in args:
            self.__sessions.open(login)
        if len(args) == 1:
            return self.do_select(login)
        return False


    def complete_open(self, text, line, begidx, endidx):
        return CommandDispatcher.CPLT_OPEN.complete(text, line, begidx, endidx)


    @_cmd
    def do_close(self, args):
        """Usage: close LOGIN...

Close each specified session."""
        if len(args) == 0:
            self.__sessions.close_current()
        else:
            for login in args:
                self.__sessions.close(login)
        if self.__sessions.current() is None:
            print('The last session has been closed.')
            return True
        return False


    def complete_close(self, text, line, begidx, endidx):
        return self.__opened_logins_cplt.complete(text, line, begidx, endidx)


    @_cmd
    def do_editor(self, args):
        """Usage: editor

Open the current submission into an IDE or editor."""
        if len(args) != 0:
            raise _BadUsageException()
        self.__sessions.current().open_editor()
        return False


    @_cmd
    def do_shell(self, args):
        """Usage: shell

Open an interactive shell in the directory of the current correcting session.
You can make any change you want in this directory and restore the original
version at any time."""
        if len(args) != 0:
            raise _BadUsageException()
        self.__sessions.current().open_shell()
        return False


    @_cmd
    def do_restore(self, args):
        """Usage: restore

Restore the current correcting session to its original state.
Any change will be lost."""
        if len(args) != 0:
            raise _BadUsageException()
        self.__sessions.restore_current()
        return False


    @_cmd
    def do_status(self, args):
        """Usage: status

Print various informations about the current submission."""
        if len(args) != 0:
            raise _BadUsageException()
        print('Basic checks:')
        self.__sessions.current().problems().print_all(1)
        return False


    @_cmd
    def do_summary(self, args):
        """Usage: summary

Print a summary of the status of all opened submissions."""
        if len(args) != 0:
            raise _BadUsageException()
        self.__sessions.print_summary()
        return False


    @_cmd
    def do_readme(self, args):
        """Usage: readme

Prints the content of README for the current submission."""
        if len(args) != 0:
            raise _BadUsageException()
        print(self.__sessions.current().readme())
        return False


    @_cmd
    def do_authors(self, args):
        """Usage: authors

Prints the content of AUTHORS for the current submission."""
        if len(args) != 0:
            raise _BadUsageException()
        print(self.__sessions.current().authors())
        return False


    @_cmd
    def do_tree(self, args):
        """Usage: tree

Prints the file tree for the current submission."""
        if len(args) != 0:
            raise _BadUsageException()
        root = self.__sessions.current().submission().local_dir()
        run_shell_command('tree -aCI ".git|.gitignore" '+root+' | less -R')
        return False


    @_cmd
    def do_test(self, args):
        """Usage: test

Run the test suite."""
        if len(args) != 0:
            raise _BadUsageException()
        self.__sessions.current().test()
        return False


    @_cmd
    def do_trish(self, args):
        """Usage: trish [LOGIN LOGIN...]

Runs the Trish program and prints a ranking of the worst cheaters."""
        if len(args) != 0 and len(args) < 2:
            raise _BadUsageException()
        logins = set(args) if len(args) != 0 else None
        scores = []
        session_count = len(self.__sessions.list())
        for i in range(session_count):
            sessionA = self.__sessions.list()[i]
            loginA = sessionA.submission().login()
            print_info(f'Matching {loginA} to other submissions...',
                       percent_pos=i,
                       percent_max=session_count)
            if logins is not None and loginA not in logins:
                continue
            for j in range(i + 1, len(self.__sessions.list())):
                sessionB = self.__sessions.list()[j]
                loginB = sessionB.submission().login()
                if logins is not None and loginB not in logins:
                    continue
                try:
                    score = CorrectingSession.run_trish(sessionA, sessionB)
                    scores.append((score, sessionA, sessionB))
                except Exception as e:
                    loginA = sessionA.submission().login()
                    loginB = sessionB.submission().login()
                    print_error(f'Trish failed to compare {loginA} and {loginB}: {e}')
        scores.sort(key=lambda x: x[0])
        for score, sessionA, sessionB in scores:
            loginA = sessionA.submission().login()
            loginB = sessionB.submission().login()
            print_info(f'{score}: {loginA} // {loginB}')
        return False


    @_cmd
    def do_exit(self, args):
        """Usage: exit

Close the correcting session.
WARNING: Any modification made to the correction trees will be lost."""
        if len(args) != 0:
            raise _BadUsageException()
        return True


    def default(self, cmd):
        if cmd == 'EOF':
            print('exit')
            return True
        print_error(str(cmd).split(' ')[0] + ': no such command')
        return False


def cmd_correct(tp_slug, logins, get_rendus):
    """
    Start the correction tool
    :param tp_slug: Slug of the TP to correct
    :param logins: List of student logins
    :param get_rendus: Should we call get before correct?
    """
    if get_rendus:
        cmd_get(tp_slug, logins, None)

    logins = list({ login for login in logins })

    tp = Tp(tp_slug)
    moulinette = tp.get_moulinette(DownloadPolicy.IF_REQUIRED)
    sessions = CorrectingSessionSet(moulinette)

    for i, login in enumerate(logins):
        try:
            print_info(
                'Processing submission of {0}...'.format(login),
                percent_pos=i,
                percent_max=len(logins),
                end=' ')
            sessions.open(login)
            print_success('Done.')
        except Exception:
            print_current_exception()

    print_info('Done.')

    if sessions.current() is not None:
        dispatcher = CommandDispatcher(sessions)
        readline_history.push(CORRECTION_HISTORY_FILE, HISTORY_SIZE)
        try:
            dispatcher.cmdloop()
        finally:
            readline_history.pop()

    return EXIT_SUCCESS


CPLT = CmdCompletor(
    [ '-g', '--get', '--no-rider' ],
    { '--file=': enum_files },
    [ enum_tp_slugs, enum_logins_for_tp ])

def cplt_correct(text, line, begidx, endidx):
    return CPLT.complete(text, line, begidx, endidx)
