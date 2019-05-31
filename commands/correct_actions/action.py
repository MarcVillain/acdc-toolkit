class Action:
    def should_run(self, key):
        return False

    def requires_student_folder(self):
        return True

    def run(self, login, login_path, project, project_path):
        pass

    def __str__(self):
        return ""
