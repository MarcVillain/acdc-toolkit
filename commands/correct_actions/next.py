from . import action


class Next(action.Action):
    def should_run(self, key):
        return key == 'n' or key == 'N'

    def requires_student_folder(self):
        return False

    def run(self, login, login_path, project, project_path):
        return 1

    def __str__(self):
        return "N: NEXT"
