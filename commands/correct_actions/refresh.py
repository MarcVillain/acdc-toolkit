from . import action


class Refresh(action.Action):
    def should_run(self, key):
        return key == 'f' or key == 'F'

    def requires_student_folder(self):
        return False

    def __str__(self):
        return "F: REFRESH"
