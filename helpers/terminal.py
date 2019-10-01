from helpers.command import run_shell_command, exec_in_folder, run_command_detached
from misc.printer import print_warning


def open_subshell(location):
    print()
    print_warning('Press Ctrl+D to get back.')
    print()

    exec_in_folder(location,
                   run_shell_command, "bash")
