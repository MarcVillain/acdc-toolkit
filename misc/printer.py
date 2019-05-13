import readline


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


def print_ask(msg, indent=0):
    print_colored_icon("\033[36m", None, msg + " [y/n]", indent=indent, end=" ")
    line = input().lower()
    readline.remove_history_item(readline.get_current_history_length() - 1)

    while line != "y" and line != "n":
        if line == "":
            print()
        print_error("Please insert 'y' or 'n':", indent=indent, end=" ")
        line = input().lower()
        readline.remove_history_item(readline.get_current_history_length() - 1)

    return line == "y"


def print_press_enter(msg, indent=0):
    print_colored_icon("\033[36m", None, "Press [Enter] " + msg + "...", indent=indent, end="")
    input()
    readline.remove_history_item(readline.get_current_history_length() - 1)
