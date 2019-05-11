from . import action


class Exit(action.Action):
    def __str__(self):
        return "Ctrl+D: EXIT"
