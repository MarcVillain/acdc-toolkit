import os
import shutil
from abc import ABC, abstractmethod
from misc.config import CAMLTRACER_REPO, CAMLTRACER_COMMIT, CAMLTRACER_LOCAL_DIR, CAMLTRACER_SETUP_PATCH_FILE, TRISH_REPO, TRISH_COMMIT, TRISH_LOCAL_DIR
from misc.printer import print_info
from helpers.command import run_command
from helpers.git import git_clone


class ExternalTool(ABC):
    def __init__(self, name, may_download):
        if not self._is_up_to_date():
            if may_download:
                print_info(f'{name} is outdated, uninstalling old version...')
                self._uninstall()
            else:
                raise  # TODO
        if not self._is_installed():
            if may_download:
                print_info(f'Installing {name}...')
                self._install()
            else:
                raise  # TODO

    @abstractmethod
    def _is_up_to_date(self):
        pass

    @abstractmethod
    def _is_installed(self):
        pass

    @abstractmethod
    def _install(self):
        pass

    @abstractmethod
    def _uninstall(self):
        pass


class CamlTracer(ExternalTool):
    def __init__(self, may_download):
        super().__init__('CamlTracer', may_download)

    def require():
        return CamlTracer(True)

    def run(self):
        test_file = os.path.join(CAMLTRACER_LOCAL_DIR, 'tests.py')
        run_command(f'camltracer trace --json {test_file} .')

    def _is_up_to_date(self):
        if run_command(f'which camltracer').returncode != 0:
            return False
        result = run_command(f'git -C {CAMLTRACER_LOCAL_DIR} rev-parse HEAD')
        return result.stdout == CAMLTRACER_COMMIT

    def _is_installed(self):
        return os.path.isdir(CAMLTRACER_LOCAL_DIR)

    def _install(self):
        git_clone(
            CAMLTRACER_REPO,
            CAMLTRACER_LOCAL_DIR,
            commit=CAMLTRACER_COMMIT)
        setup_script = os.path.join(CAMLTRACER_LOCAL_DIR, 'setup.py')
        run_command(
            f'patch {setup_script} {CAMLTRACER_SETUP_PATCH_FILE}'
        ).check_returncode()
        run_command(
            f'pip install {CAMLTRACER_LOCAL_DIR}'
        ).check_returncode()

    def _uninstall(self):
        run_command(f'pip uninstall -y camltracer')
        try:
            shutil.rmtree(CAMLTRACER_LOCAL_DIR)
        except FileNotFoundError:
            pass


class Trish(ExternalTool):
    def __init__(self, may_download):
        super().__init__('Trish', may_download)

    def require():
        return Trish(True)

    def cmp_files(self, fileA, fileB):
        output = run_command(f'trish "{fileA}" "{fileB}"')
        output.check_returncode()
        return float(output.stdout)

    def _is_up_to_date(self):
        if run_command(f'which trish').returncode != 0:
            return False
        result = run_command(f'git -C {TRISH_LOCAL_DIR} rev-parse HEAD')
        return result.stdout == TRISH_COMMIT

    def _is_installed(self):
        return os.path.isdir(TRISH_LOCAL_DIR)

    def _install(self):
        git_clone(TRISH_REPO, TRISH_LOCAL_DIR, commit=TRISH_COMMIT)
        run_command(
            f'pip install {TRISH_LOCAL_DIR}'
        ).check_returncode()

    def _uninstall(self):
        run_command(f'pip uninstall -y trish')
        try:
            shutil.rmtree(TRISH_LOCAL_DIR)
        except FileNotFoundError:
            pass
