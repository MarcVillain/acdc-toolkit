import sys
import os
import shutil
import re
from enum import Enum, auto
from abc import ABC, abstractmethod
from xml.etree import cElementTree

from misc.config import MOULINETTE_FOLDER, MOULINETTE_REPO, CORRECTIONS_FOLDER
from helpers.git import git_clone
from helpers.io import folder_find, folder_ls, parent_dir
from helpers.command import run_command_detached, run_command
from helpers.terminal import open_subshell
from misc.printer import print_success, print_warning, print_error


class DownloadPolicy(Enum):
    NEVER = auto()
    IF_REQUIRED = auto()
    ALWAYS = auto()


class ResourceNotFoundException(Exception):
    pass


class Moulinette(ABC):
    """
    Represents a downloaded moulinette.
    Objects of this class should not be directly instanciated. Use
    the Tp class for this purpose.
    """
    def __init__(self, tp):
        self._tp = tp


    def tp(self):
        return self._tp


    @abstractmethod
    def new_correcting_session(self, submission):
        pass


    def get_for_tp(tp, dl_policy):
        local_dir = Moulinette.__local_dir_for_tp(tp)
        overwriting = False
        if os.path.exists(local_dir):
            if dl_policy is DownloadPolicy.ALWAYS:
                overwriting = True
            else:
                return Moulinette.__get_local_for_tp(tp)
        elif dl_policy is DownloadPolicy.NEVER:
            raise ResourceNotFoundException('Moulinette not available locally.')

        # Downloading
        dl_path = to_tmp_path(local_dir) if overwriting else local_dir
        try:
            git_clone(Moulinette.__url_for_tp(tp), dl_path)
        except Exception as e:
            if overwriting:
                shutil.rmtree(dl_path)
            raise
        if overwriting:
            shutil.rmtree(local_dir)
            os.rename(dl_path, local_dir)

        return Moulinette.__get_local_for_tp(tp)


    def remove_locally_for_tp(tp):
        local_dir = Moulinette.__local_dir_for_tp(tp)
        if os.path.isdir(local_dir):
            shutil.rmtree(local_dir)
            return True
        else:
            return False


    def _local_dir(self):
        return Moulinette.__local_dir_for_tp(self.tp())


    def __local_dir_for_tp(tp):
        return os.path.join(MOULINETTE_FOLDER, tp.slug())


    def __url_for_tp(tp):
        return MOULINETTE_REPO.format(tp_slug=tp.slug())


    def __get_local_for_tp(tp):
        return _CsMoulinette(tp)


class _CsMoulinette(Moulinette):
    def __init__(self, tp):
        super().__init__(tp)


    def new_correcting_session(self, submission):
        return _CsCorrectingSession(submission)


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


class _CsCorrectingSession:
    # Private attributes:
    #   * __submission: Submission
    #   * __moulinette: Moulinette
    #   * __dir: str
    #   * __project_dirs
    #   * __problems: ProblemLog
    #   * __reamde: str
    #   * __authors: str
    def __init__(self, submission):
        self.__submission = submission
        self.__moulinette = \
            self.__submission.tp().get_moulinette(DownloadPolicy.NEVER)

        self.__problems = ProblemLog()

        self.__readme = _read_readme(self.__submission, self.__problems)
        self.__authors = _read_authors(self.__submission, self.__problems)

        self.__dir = os.path.join(
            CORRECTIONS_FOLDER,
            self.__submission.tp().slug()+'-'+self.__submission.login())
        if os.path.isdir(self.__dir):
            self.__load_session()
        else:
            self.__init_session()


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


    def open_editor(self):
        for sln in folder_find(self.__dir, includes=['.*\\.sln']):
            run_command_detached('rider '+sln)


    def open_shell(self):
        open_subshell(self.__dir)


    def __build(self, project_dir, pb_item):
        csproj_files = folder_find(project_dir, includes=['.*\\.csproj'])
        if len(csproj_files) != 1:
            self.__problems.add(pb_item, 'wrong .csproj count')
        else:
            res = run_command('msbuild \'{}\''.format(csproj_files[0]))
            if res.returncode != 0:
                self.__problems.add(pb_item, 'build failed')


    def __get_project_dirs(self):
        csproj_files = [
            path
            for path in
            folder_find(
                self.dir(),
                includes=['.*\\.csproj'],
                excludes=['\\..*', '.*Tests.*', '.*Correction.*'],
                depth=3)
            if path.endswith('.csproj') ]
        project_dirs = [ os.path.dirname(path) for path in csproj_files ]
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
        self.__project_dirs.append(dest_dir)
        project_name = os.path.basename(dest_dir)
        pb_item =  'Project "{0}"'.format(project_name)
        self.__problems.add(pb_item)
        src_dir = os.path.join(self.__submission.local_dir(), project_name)
        if not os.path.isdir(src_dir):
            self.__problems.add(pb_item, 'not found')
            return
        # Copying files
        pending = [ os.path.curdir ]
        while len(pending) > 0:
            cur_src_dir = os.path.join(src_dir, pending.pop())
            for entry in os.listdir(cur_src_dir):
                src = os.path.join(cur_src_dir, entry)
                dest = os.path.join(dest_dir, entry)
                if os.path.isdir(src):
                    os.makedirs(dest)
                    pending.append(entry)
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
            self.__problems.add(pb_item, 'stray bin/')
            shutil.rmtree(bin_path)
        obj_path = os.path.join(dest_dir, project_name, 'obj')
        if os.path.exists(obj_path):
            self.__problems.add(pb_item, 'stray obj/')
            shutil.rmtree(obj_path)
        self.__build(dest_dir, pb_item)


    def __session_file(self):
        return os.path.join(self.__dir, '.session')


    def __load_session(self):
        tree = cElementTree.parse(self.__session_file()).getroot()
        self.__readme = tree.find('readme').text
        self.__authors = tree.find('authors').text
        self.__project_dirs = []
        for e in tree.findall('project-dir'):
            self.__project_dirs.append(e.text)
        self.__problems = ProblemLog.read_from_tree(tree.find('problems'))


    def __init_session(self):
        shutil.copytree(self.__moulinette._local_dir(), self.dir())
        shutil.rmtree(os.path.join(self.dir(), '.git'))
        self.__project_dirs = []
        for project_dir in self.__get_project_dirs():
            self.__init_project(project_dir)

        # Saving state
        xml = cElementTree.TreeBuilder()
        xml.start('correcting-session')
        xml.start('readme')
        xml.data(self.__readme)
        xml.end('readme')
        xml.start('authors')
        xml.data(self.__authors)
        xml.end('authors')
        for project_dir in self.__project_dirs:
            xml.start('project-dir')
            xml.data(project_dir)
            xml.end('project-dir')
        xml.start('problems')
        self.problems().write_to_tree_builder(xml)
        xml.end('problems')
        xml_str = cElementTree.tostring(xml.end('correcting-session'))
        with open(self.__session_file(), 'bw+') as session_file:
            session_file.write(xml_str)
