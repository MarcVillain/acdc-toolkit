import sys
if __debug__:
    import traceback

from helpers.readline_history import readline_history


def print_colored_icon(color, icon, msg, indent=0, end='\n'):
    icon_spaced = ""
    if icon is not None:
        icon_spaced = icon + " "

    print(" " * indent * 4 + color + icon_spaced + str(msg) + "\033[0m", end=end)


def print_success(msg, indent=0, end='\n'):
    print_colored_icon("\033[32m", "✓", msg, indent=indent, end=end)


def print_error(msg, indent=0, end='\n'):
    print_colored_icon("\033[31m", "✗", msg, indent=indent, end=end)


def print_warning(msg, indent=0, end='\n'):
    print_colored_icon("\033[33m", "!", msg, indent=indent, end=end)


def print_debug(msg, indent=0, end='\n'):
    if __debug__:
        print_colored_icon("\033[37m", "⚐", msg, indent=indent, end=end)


def print_current_exception():
    if __debug__:
        print_error('An exception occured:')
        traceback.print_exc()
    else:
        print_error(sys.exc_info()[1])


def print_info(msg, indent=0, end='\n', percent_pos=-1, percent_max=-1):
    icon = "»"
    if percent_pos != -1:
        percent = 100
        if percent_max > 1:
            if percent_pos == 0:
                percent = 0
            elif percent_pos != percent_max - 1:
                percent = int(percent_pos * 100 / (percent_max - 1))

        icon = str(percent).rjust(3, " ") + "% " + icon

    print_colored_icon("\033[37m", icon, msg, indent=indent, end=end)


def print_ask(msg, options, indent=0):
    print_colored_icon("\033[36m", None, msg + " [" + "/".join(options) + "]", indent=indent, end=" ")
    line = input().lower()
    readline_history.remove_last_entry()

    error = ''
    if len(options) == 1:
        error = "'" + options[0] + "'"
    elif len(options) > 1:
        error = ', '.join("'" + option + "'" for option in options[:-1]) + " or '" + options[-1] + "'"

    while line not in options:
        if line == "":
            print()
        print_error("Please insert " + error + ":", indent=indent, end=" ")
        line = input().lower()
        readline_history.remove_last_entry()

    return line


def print_ask_yes_no(msg, indent=0):
    return print_ask(msg, ['y', 'n'], indent=indent) == 'y'


def print_press_enter(msg, indent=0):
    print_colored_icon("\033[36m", None, "Press [Enter] " + msg + "...", indent=indent, end="")
    input()
    readline_history.remove_last_entry()
