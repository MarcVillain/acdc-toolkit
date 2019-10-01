import os
import shlex
import subprocess
from misc.printer import print_debug


def run_command(cmd):
    """
    Execute a shell command
    :param cmd: The command to run
    :return: The return value of the subprocess
    """
    print_debug('Command: ' + cmd)
    res = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res.stdout = res.stdout.decode('utf-8')[:-1]
    res.stderr = res.stderr.decode('utf-8')[:-1]
    return res


def run_shell_command(cmd):
    return subprocess.call(cmd, shell=True)


def run_command_detached(cmd):
    devnull = open(os.devnull)
    subprocess.Popen(shlex.split(cmd), stdout=devnull, stderr=devnull)


def run_commands(cmds, cmds_fail=None, cmds_finally=None):
    """
    Execute multiple shell commands
    :param cmds: The list of commands to execute
    :param cmds_fail: The commands to execute on fail
    :param cmds_finally: The commands to execute at the end whatever happens
    :return: The return value of the last command of 'cmds'
    """
    if cmds_finally is None:
        cmds_finally = []
    if cmds_fail is None:
        cmds_fail = []
    ret_val = None

    # Run every command
    for cmd in cmds:
        ret_val = run_command(cmd)
        # Run fail commands on fail
        if ret_val.returncode is not 0:
            for cmd_fail in cmds_fail:
                run_command(cmd_fail)
            break

    # Run finally commands
    for cmd_finally in cmds_finally:
        run_command(cmd_finally)

    return ret_val


def exec_in_folder(folder_path, func, *func_args):
    dir_backup = os.getcwd()
    os.chdir(folder_path)
    res = 1
    try:
        res = func(*func_args)
    except Exception as e:
        os.chdir(dir_backup)
        raise e

    os.chdir(dir_backup)
    return res
