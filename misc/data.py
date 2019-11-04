import os
import re
import shutil

from misc.printer import print_warning
from misc.config import STUDENTS_FOLDER, REPO_FOLDER, REPO_URL
from helpers.other import format_to_regex
from helpers.io import folder_ls
from misc.moulinettes import Moulinette, Language


class Tp:
    def __init__(self, slug):
        self._slug = slug


    def __eq__(self, other):
        return isinstance(other, Tp) and self.slug() == other.slug()


    def slug(self):
        return self._slug


    def language(self):
        if self._slug.startswith('caml'):
            return Language.OCAML
        else:
            return Language.C_SHARP


    def _local_dir(self):
        return os.path.join(STUDENTS_FOLDER, self.slug())


    def has_local_submissions(self):
        """ Similar to len(tp.get_local_submissions()) == 0 """
        local_dir = self._local_dir()
        return os.path.isdir(local_dir) and len(os.listdir(local_dir)) != 0


    def get_moulinette(self, dl_policy):
        return Moulinette.get_for_tp(self, dl_policy)


    def remove_moulinette_locally(self):
        return Moulinette.remove_locally_for_tp(self)


    def get_local_submissions(self):
        submissions = []
        if os.path.exists(self._local_dir()):
            regex = '^' + format_to_regex(
                REPO_FOLDER, tp_slug=re.escape(self.slug()), login='.*') + '$'
            for entry in os.listdir(self._local_dir()):
                match = re.search(regex, entry)
                if match is None or len(match.group('login')) == 0:
                    print_warning(
                        'Invalid directory name: '
                        + os.path.join(self.local_dir(), entry))
                else:
                    submissions.append(Submission(self, match.group('login')))
        return submissions


    def remove_locally(self):
        local_dir = self._local_dir()
        if os.path.isdir(local_dir):
            shutil.rmtree(local_dir)
            return True
        else:
            return False


    def get_local_tps():
        if os.path.isdir(STUDENTS_FOLDER):
            tps = [ Tp(entry) for entry in os.listdir(STUDENTS_FOLDER) ]
            tps.sort(key=Tp.slug)
            return tps
        else:
            return []


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


    def __eq__(self, other):
        return \
            isinstance(other, Submission) \
            and self.tp() == other.tp() \
            and self.login() == other.login()


    def tp(self):
        return self._tp


    def login(self):
        return self._login


    def name(self):
        return self.tp().slug()+'/'+self.login()


    def local_dir(self):
        return os.path.join(
            self.tp()._local_dir(),
            REPO_FOLDER.format(tp_slug=self.tp().slug(), login=self.login()))


    def exists_locally(self):
        return os.path.exists(self.local_dir())


    def url(self):
        return REPO_URL.format(login=self.login(), tp_slug=self.tp().slug())


    def remove_locally(self):
        if self.exists_locally():
            shutil.rmtree(self.local_dir())
            if not self.tp().has_local_submissions():
                self.tp().remove_locally()
            return True
        else:
            return False
