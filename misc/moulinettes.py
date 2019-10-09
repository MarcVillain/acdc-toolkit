import sys
import os
import shutil
import re
import json
import enum
from abc import ABC, abstractmethod
from xml.etree import cElementTree

from misc.config import MOULINETTE_FOLDER, MOULINETTE_REPO, CORRECTIONS_FOLDER, CAMLTRACER_REPO, CAMLTRACER_RELEASE_TAG, CAMLTRACER_LOCAL_DIR, CAMLTRACER_SETUP_PATCH_FILE, TRISH_INSTALL_CMD
from helpers.git import git_clone
from helpers.io import folder_find, folder_ls, parent_dir
from helpers.command import run_command_detached, run_command, exec_in_folder
from helpers.terminal import open_subshell
from misc.printer import print_success, print_warning, print_error


class Language(enum.Enum):
    C_SHARP = enum.auto()
    OCAML = enum.auto()


class DownloadPolicy(enum.Enum):
    NEVER = enum.auto()
    IF_REQUIRED = enum.auto()
    ALWAYS = enum.auto()


class ResourceNotFoundException(Exception):
    pass


class Moulinette(ABC):
    """
    Represents a downloaded moulinette.
    Objects of this class should not be directly instanciated. Use
    the Tp class for this purpose.
    """
    def __init__(self, tp, dl_policy):
        self._tp = tp


    def tp(self):
        return self._tp


    @abstractmethod
    def new_correcting_session(self, submission):
        pass


    def remove_locally(self):
        pass


    def get_for_tp(tp, dl_policy):
        if tp.language() == Language.OCAML:
            return _CamlMoulinette(tp, dl_policy)
        elif tp.language() == Language.C_SHARP:
            return _CsMoulinette(tp, dl_policy)
        raise


    def remove_locally_for_tp(tp):
        try:
            moulinette = Moulinette.get_for_tp(tp, DownloadPolicy.NEVER)
            moulinette.remove_locally()
        except ResourceNotFoundException:
            pass


def _find_file(submission, problems, name, name_re):
    submission_dir = submission.local_dir()
    # Correct
    expected_path = os.path.join(submission_dir, name)
    if os.path.isfile(expected_path):
        return expected_path
    # Wrong name
    for entry in os.listdir(submission_dir):
        if name_re.match(entry) is not None:
            problems.add(name, 'wrong name')
            return os.path.join(submission_dir, entry)
    # Wrong location
    found = folder_find(submission_dir, includes=['README'])
    if len(found) > 0:
        problems.add(name, 'wrong location')
        return found
    # Wrong name & location
    for root, dirs, files in os.walk(submission_dir):
        for entry in files:
            if name_re.match(entry):
                problems.add(name, 'wrong name')
                problems.add(name, 'wrong location')
                return os.path.join(submission_dir, entry)
    # Not found
    problems.add(name, 'missing')
    return None


class ProblemLog:
    def __init__(self):
        self.__dic = {}


    def add(self, item, error=None):
        if not item in self.__dic:
            self.__dic[item] = []
        if error is not None:
            self.__dic[item].append(error)


    def print_all(self, indent=0):
        for item in self.__dic:
            if len(self.__dic[item]) == 0:
                print_success(item+': ok', indent)
            else:
                print_warning(item+': '+(', '.join(self.__dic[item])), indent)


    def print_one_liner(self):
        error_count = 0
        for item in self.__dic:
            error_count += len(self.__dic[item])
        if error_count == 0:
            print_success('No problems.')
        elif error_count == 1:
            print_warning('1 problem.')
        else:
            print_warning(str(error_count)+' problems.')


    def write_to_tree_builder(self, xml):
        for item in self.__dic:
            xml.start('item')
            xml.start('name')
            xml.data(item)
            xml.end('name')
            for problem in self.__dic[item]:
                xml.start('problem')
                xml.data(problem)
                xml.end('problem')
            xml.end('item')


    def read_from_tree(tree):
        problems = ProblemLog()
        for e in tree.findall('item'):
            item = e.find('name').text
            problems.__dic[item] = []
            for f in e.findall('problem'):
                problems.__dic[item].append(f.text)
        return problems


def _file_insert_text_every_n_lines(file_path, text, n):
    f = open(file_path, "r")
    contents = f.readlines()
    f.close()

    i = 0
    while i < len(contents):
        for line in text.split("\n"):
            contents.insert(i, line + "\n")
            i += 1
        i += n

    f = open(file_path, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()


def _read_readme(submission, problems):
    problems.add('README')
    submission_dir = submission.local_dir()
    path = _find_file(
        submission, problems,
        'README',
        re.compile(r'^READ[ _-]?ME(\\..+)?$', re.IGNORECASE))
    if path is None:
        return ''
    with open(path, 'r') as f:
        content = f.read()
    if len(content) == 0:
        problems.add('README', 'empty')
    elif re.match('^\s*$', content):
        problems.add('README', 'whitespaces only')
    return content


def _read_authors(submission, problems):
    problems.add('AUTHORS')
    submission_dir = submission.local_dir()
    path = _find_file(
        submission, problems,
        'AUTHORS',
        re.compile(r'^AUTHORS?(\\..+)?$', re.IGNORECASE))
    if path is None:
        return ''
    with open(path, 'r') as f:
        content = f.read()
    if len(content) == 0:
        problems.add('AUTHORS', 'empty')
    elif not content == '* '+submission.login()+'\n':
        problems.add('AUTHORS', 'not conform')
    return content


class CorrectingSession(ABC):
    # Private attributes:
    #   * __submission: Submission
    #   * __moulinette: Moulinette
    #   * __dir: str
    #   * __problems: ProblemLog
    #   * __reamde: str
    #   * __authors: str
    def __init__(self, submission):
        self.__submission = submission
        self.__moulinette = \
            self.submission().tp().get_moulinette(DownloadPolicy.NEVER)

        self.__problems = ProblemLog()

        self.__readme = _read_readme(self.submission(), self.problems())
        self.__authors = _read_authors(self.submission(), self.problems())

        self.__dir = os.path.join(
            CORRECTIONS_FOLDER,
            self.submission().tp().slug()+'-'+self.submission().login())
        if os.path.isdir(self.__dir):
            saved = cElementTree.parse(self.__session_file()).getroot()
            self._load_session(saved)
        else:
            try:
                self._init_session()
            except:
                if os.path.isdir(self.dir()):
                    shutil.rmtree(self.dir())
                raise
            self.save()


    def __session_file(self):
        return os.path.join(self.__dir, '.session')


    def save(self):
        save = cElementTree.TreeBuilder()
        save.start('correcting-session')
        self._save_session(save)
        xml_str = cElementTree.tostring(save.end('correcting-session'))
        with open(self.__session_file(), 'bw+') as session_file:
            session_file.write(xml_str)


    def moulinette(self):
        return self.__moulinette


    def remove(self):
        shutil.rmtree(self.dir())
        self.__dir = None


    def submission(self):
        return self.__submission


    def dir(self):
        assert self.__dir is not None
        return self.__dir


    def readme(self):
        assert self.__readme is not None
        return self.__readme


    def authors(self):
        assert self.__authors is not None
        return self.__authors


    def problems(self):
        assert self.__problems is not None
        return self.__problems


    @abstractmethod
    def open_editor(self):
        pass


    def open_shell(self):
        open_subshell(self.__dir)


    def _load_session(self, saved):
        self.__readme = saved.find('readme').text
        if self.__readme is None:
            self.__readme = ''
        self.__authors = saved.find('authors').text
        if self.__authors is None:
            self.__authors = ''
        self.__problems = ProblemLog.read_from_tree(saved.find('problems'))


    def _save_session(self, save):
        save.start('readme')
        save.data(self.__readme)
        save.end('readme')
        save.start('authors')
        save.data(self.__authors)
        save.end('authors')
        save.start('problems')
        self.problems().write_to_tree_builder(save)
        save.end('problems')


    @abstractmethod
    def _init_session(self):
        pass


    @abstractmethod
    def _get_submitted_source_files(self):
        pass


    def run_trish(sessionA, sessionB):
        if shutil.which('trish') is None:
            run_command(TRISH_INSTALL_CMD)
        score = 0
        for fileA in sessionA._get_submitted_source_files():
            fileB = os.path.join(
                sessionB.submission().local_dir(),
                os.path.relpath(fileA, sessionA.submission().local_dir()))
            if os.path.isfile(fileB):
                output = run_command(f'trish "{fileA}" "{fileB}"')
                output.check_returncode()
                score += float(output.stdout)
        return score


class _CsMoulinette(Moulinette):
    def __init__(self, tp, dl_policy):
        super().__init__(tp, dl_policy)

        self.__local_dir = os.path.join(MOULINETTE_FOLDER, tp.slug())
        overwriting = False

        if os.path.exists(self.__local_dir):
            if dl_policy is DownloadPolicy.ALWAYS:
                overwriting = True
            else:
                return
        elif dl_policy is DownloadPolicy.NEVER:
            raise ResourceNotFoundException('Moulinette not available locally.')

        # Downloading
        if overwriting:
            dl_path = to_tmp_path(self.__local_dir)
        else:
            dl_path = self.__local_dir
        try:
            url = MOULINETTE_REPO.format(tp_slug=tp.slug())
            git_clone(url, dl_path)
        except Exception as e:
            if overwriting:
                shutil.rmtree(dl_path)
            raise
        if overwriting:
            shutil.rmtree(self.__local_dir)
            os.rename(dl_path, self.__local_dir)


    def _local_dir(self):
        return self.__local_dir


    def remove_locally(self):
        if os.path.isdir(self.__local_dir):
            shutil.rmtree(self.__local_dir)
            return True
        else:
            return False


    def new_correcting_session(self, submission):
        return _CsCorrectingSession(submission)


class _CsCorrectingSession(CorrectingSession):
    # Private attributes:
    #   * __project_dirs


    def open_editor(self):
        super().open_editor()
        for sln in folder_find(self.dir(), includes=['.*\\.sln']):
            run_command_detached('rider '+sln)


    def __build(self, project_dir, pb_item):
        csproj_files = folder_find(project_dir, includes=['.*\\.csproj'])
        if len(csproj_files) != 1:
            self.problems().add(pb_item, 'wrong .csproj count')
        else:
            res = run_command('msbuild \'{}\''.format(csproj_files[0]))
            if res.returncode != 0:
                self.problems().add(pb_item, 'build failed')


    def __get_project_dirs(self):
        sln_files = [
            path
            for path in
            folder_find(
                self.dir(),
                excludes=['\\..*', '.*Tests.*', '.*Correction.*'],
                depth=3)
            if path.endswith('.sln') ]
        project_dirs = [ os.path.dirname(path) for path in sln_files ]
        project_dirs.sort(key=os.path.basename)
        return project_dirs


    def __adjust_code(self, cs_file):
        replace_table = {
            re.compile(r'\bprivate\b'): 'public',
            re.compile(r'\bprotected\b'): 'public',
            re.compile(r'\binternal\b'): 'public',
            re.compile(r'\bpublic\s+set\b'): 'set'
        }

        with open(cs_file, 'r') as f:
            content = f.read()
        for regex in replace_table:
            content = re.sub(regex, replace_table[regex], content)
        with open(cs_file, 'w') as f:
            f.write(content)

        _file_insert_text_every_n_lines(
            cs_file,
            '// '+self.submission().login(),
            20)


    def __init_project(self, dest_dir):
        """
        Register a project and copy its files into the session
        directory. Also check for common mistakes in source trees.
        """
        assert(os.path.isdir(dest_dir))
        self.__project_dirs.append(dest_dir)
        project_name = os.path.basename(dest_dir)
        pb_item =  'Project "{0}"'.format(project_name)
        self.problems().add(pb_item)
        src_dir = os.path.join(self.submission().local_dir(), project_name)
        if not os.path.isdir(src_dir):
            self.problems().add(pb_item, 'not found')
            return
        # Copying files
        pending = [ (src_dir, dest_dir) ]
        while len(pending) > 0:
            cur_src_dir, cur_dest_dir = pending.pop()
            for entry in os.listdir(cur_src_dir):
                src = os.path.join(cur_src_dir, entry)
                dest = os.path.join(cur_dest_dir, entry)
                if os.path.isdir(src):
                    if not os.path.exists(dest):
                        os.makedirs(dest)
                    if os.path.isdir(dest):
                        pending.append((src, dest))
                else:
                    shutil.copy(src, dest)
        # Adjusting files
        for cs_file in folder_find(
                dest_dir,
                includes=['.*\\.cs'],
                excludes=['AssemblyInfo.cs']):
            self.__adjust_code(cs_file)
        bin_path = os.path.join(dest_dir, project_name, 'bin')
        if os.path.exists(bin_path):
            self.problems().add(pb_item, 'stray bin/')
            shutil.rmtree(bin_path)
        obj_path = os.path.join(dest_dir, project_name, 'obj')
        if os.path.exists(obj_path):
            self.problems().add(pb_item, 'stray obj/')
            shutil.rmtree(obj_path)
        self.__build(dest_dir, pb_item)


    def _load_session(self, saved):
        super()._load_session(saved)
        self.__project_dirs = []
        for e in saved.findall('project-dir'):
            self.__project_dirs.append(e.text)


    def _save_session(self, save):
        super()._save_session(save)
        for project_dir in self.__project_dirs:
            save.start('project-dir')
            save.data(project_dir)
            save.end('project-dir')


    def _init_session(self):
        super()._init_session()
        shutil.copytree(self.moulinette()._local_dir(), self.dir())
        shutil.rmtree(os.path.join(self.dir(), '.git'))
        self.__project_dirs = []
        for project_dir in self.__get_project_dirs():
            self.__init_project(project_dir)


    def _get_submitted_source_files(self):
        return folder_find(
            self.submission().local_dir(),
            includes=['.*\\.cs'],
            excludes=['AssemblyInfo.cs'])


class _CamlMoulinette(Moulinette):
    def __init__(self, tp, dl_policy):
        super().__init__(tp, dl_policy)
        self.__dir = CAMLTRACER_LOCAL_DIR
        if not os.path.isdir(CAMLTRACER_LOCAL_DIR):
            _CamlMoulinette.__install_camltracer()


    def new_correcting_session(self, submission):
        return _CamlCorrectingSession(submission)


    def _run_in_current_dir(self):
        run_command('acdc-camltracer trace --json {} .'.format(
            os.path.join(self.__dir, 'tests.py')))


    def __install_camltracer():
        git_clone(CAMLTRACER_REPO, CAMLTRACER_LOCAL_DIR, CAMLTRACER_RELEASE_TAG)
        run_command('patch {} {}'.format(
            os.path.join(CAMLTRACER_LOCAL_DIR, 'setup.py'),
            CAMLTRACER_SETUP_PATCH_FILE))
        run_command('pip install '+CAMLTRACER_LOCAL_DIR)


class _CamlCorrectingSession(CorrectingSession):
    # Private attributes:
    #   * __project_dirs


    def open_editor(self):
        super().open_editor()
        if not 'EDITOR' in os.environ:
            prin_error('Cannot guess editor: please export $EDITOR')
            return
        cmd = os.environ['EDITOR']
        file_pattern = '.*\\.(ml|mli|caml|ocaml)'
        for path in folder_find(self.dir(), includes=[file_pattern]):
            cmd += ' '
            cmd += path
        run_command_detached(cmd)


    def _init_session(self):
        super()._init_session()
        shutil.copytree(self.submission().local_dir(), self.dir())
        shutil.rmtree(os.path.join(self.dir(), '.git'))
        # Running CamlTracer
        def run():
            self.moulinette()._run_in_current_dir()
        exec_in_folder(self.dir(), run)
        # Parsing report
        with open(os.path.join(self.dir(), 'report.json'), 'r') as f:
            report = json.loads(f.read())
        for exercise in report[0]['exoreports']:
            pb_item = 'Exercise "{}"'.format(exercise['name'])
            self.problems().add(pb_item)
            if not exercise['found']:
                self.problems().add(pb_item, 'not found')
            else:
                if len(exercise['errors']) != 0:
                    self.problems().add(pb_item, 'caml error')
                for func in exercise['funreports']:
                    pb_item = 'Function "{}": "{}"'.format(
                        exercise['name'],
                        func['fun'])
                    self.problems().add(pb_item)
                    if not func['found']:
                        self.problems().add(pb_item, 'not found')
                    else:
                        for warning in func['warnings']:
                            self.problems().add(pb_item, warning)
                        for test in func['cases']:
                            if not test['passed']:
                                self.problems().add(pb_item, 'test failed')
                                break


    def _get_submitted_source_files(self):
        return folder_find(
            self.submission().local_dir(),
            includes=['.*\\.(ml|mli|caml|ocaml)'])
