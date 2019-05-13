from helpers.command import run_command_detached
from misc.config import DEFAULT_LOGINS_FILE


def get_logins(file, logins=None):
    if logins is None:
        logins = []

    if len(logins) is 0 and file is None:
        file = DEFAULT_LOGINS_FILE

    if file is not None:
        for login in open(file, "r"):
            if login is "":
                continue
            logins.append(login.strip("\n\r\t "))

    for login in logins:
        if login not in logins:
            logins.append(login)

    return logins