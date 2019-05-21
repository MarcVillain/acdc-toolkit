class Action:
    def should_run(self, key):
        return False

    def can_run_if_student_folder_exists(self):
        return False

    def run(self, login, login_path, project, project_path):
        pass

    def __str__(self):
        return ""
