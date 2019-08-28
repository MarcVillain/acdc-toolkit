import os

from helpers.io import parent_dir

try:
    import readline
    readline.set_completer_delims(' ')
except ImportError:
    readline = None


class _ReadlineHistory:
    def __init__(self):
        self.__stack = []


    def push(self, hist_file, max_size):
        if len(self.__stack) > 0:
            self.save()
        self.__stack.append((hist_file, max_size))
        self.__read()


    def pop(self):
        self.save()
        self.__stack.pop()
        self.__read()


    def save(self):
        hist_file, max_size = self.__stack[-1]
        if readline:
            containing_dir = parent_dir(hist_file)
            if not os.path.isdir(containing_dir):
                os.makedirs(containing_dir)
            readline.write_history_file(hist_file)


    def remove_last_entry(self):
        if readline:
            new_length = readline.get_current_history_length() - 1
            readline.remove_history_item(new_length)


    def __read(self):
        hist_file, max_size = self.__stack[-1]
        if readline:
            readline.set_history_length(max_size)
            if os.path.exists(hist_file):
                readline.read_history_file(hist_file)


readline_history = _ReadlineHistory()
