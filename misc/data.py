import os
import re

from misc.printer import print_warning
from misc.config import MOULINETTE_FOLDER, STUDENTS_FOLDER, REPO_FOLDER, REPO_URL
from helpers.other import format_to_regex
from helpers.io import folder_ls


class Tp:
    def __init__(self, slug):
        self._slug = slug


    def slug(self):
        return self._slug


    def local_dir(self):
        return os.path.join(STUDENTS_FOLDER, self.slug())


    def local_moulinette_dir(self):
        return os.path.join(MOULINETTE_FOLDER, self.slug())


    def exists_locally(self):
        return os.path.exists(self.local_dir())


    def get_local_submissions(self):
        submissions = []
        if os.path.exists(self.local_dir()):
            regex = '^' + format_to_regex(
                REPO_FOLDER, tp_slug=re.escape(self.slug()), login='.*') + '$'
            for entry in os.listdir(self.local_dir()):
                match = re.search(regex, entry)
                if match is None or len(match.group('login')) == 0:
                    print_warning(
                        'Invalid directory name: '
                        + os.path.join(self.local_dir(), entry))
                else:
                    submissions.append(Submission(self, match.group('login')))
        return submissions


    def get_local_tps():
        return [ Tp(entry) for entry in folder_ls(STUDENTS_FOLDER)
                 if 'tp' in entry ]


class Submission:
    """
    Represents a repository containing the submission of a specific student
    for a specific TP.
    The repository exists remotely, and is associated to a local directory
    which can hold a copy.
    """
    def __init__(self, tp, login):
        if isinstance(tp, Tp):
            self._tp = tp
        else:
            self._tp = Tp(tp)
        self._login = login


    def tp(self):
        return self._tp


    def login(self):
        return self._login


    def local_dir(self):
        return os.path.join(
            self.tp().local_dir(),
            REPO_FOLDER.format(tp_slug=self.tp().slug(), login=self.login()))


    def exists_locally(self):
        return os.path.exists(self.local_dir())


    def url(self):
        return REPO_URL.format(login=self.login(), tp_slug=self.tp().slug())
