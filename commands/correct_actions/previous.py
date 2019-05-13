from . import action


class Previous(action.Action):
    def should_run(self, key):
        return key == 'p' or key == 'P'

    def run(self, login, login_path, project, project_path):
        return -1

    def __str__(self):
        return "P: PREVIOUS"
