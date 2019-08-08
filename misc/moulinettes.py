import sys
import os
import shutil
from enum import Enum, auto
from abc import ABC, abstractmethod

from misc.config import MOULINETTE_FOLDER, MOULINETTE_REPO
from helpers.git import git_clone
from helpers.io import folder_find


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
    def get_project_dirs(self):
        pass


    @abstractmethod
    def get_project_dirs(self):
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


    def get_project_dirs(self):
        local_dir = self._local_dir()
        csproj_files = [
            path
            for path in
            folder_find(local_dir,
                        includes=['.*\\.csproj'],
                        excludes=['\\..*', '.*Tests.*', '.*Correction.*'],
                        depth=3)
            if path.endswith('.csproj')]
        project_dirs = list({ os.path.dirname(path) for path in csproj_files })
        project_dirs.sort(key=os.path.basename)
        return project_dirs
