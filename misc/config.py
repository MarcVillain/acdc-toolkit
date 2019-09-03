import os

ACDC_YEAR = 2022
SUP_YEAR = ACDC_YEAR + 2

TOOLKIT_FOLDER = os.path.dirname(os.path.dirname(__file__))
RES_FOLDER = os.path.join(TOOLKIT_FOLDER, 'res')
ACDC_LOCAL_FOLDER = os.path.expanduser('@_DATA_DIR_@')

MOULINETTE_FOLDER = os.path.join(ACDC_LOCAL_FOLDER, "moulinettes")
STUDENTS_FOLDER = os.path.join(ACDC_LOCAL_FOLDER, "students")
CORRECTIONS_FOLDER = os.path.join(ACDC_LOCAL_FOLDER, "corrections")

DEFAULT_LOGINS_FILE = os.path.join(ACDC_LOCAL_FOLDER, "logins.txt")

HISTORY_FILE = os.path.join(ACDC_LOCAL_FOLDER, ".toolkit_history")
HISTORY_SIZE = 1000
CORRECTION_HISTORY_FILE = os.path.join(ACDC_LOCAL_FOLDER, ".correction_history")

REPO_FOLDER = "{tp_slug}-{login}"
REPO_URL = "git@git.cri.epita.fr:p/" + str(SUP_YEAR) + "-sup-tp/" + REPO_FOLDER
SUBMISSION_TAG = "submission"

MOULINETTE_REPO = "git@gitlab.com:acdc_epita/" + str(ACDC_YEAR) + "/{tp_slug}.git"

CAMLTRACER_REPO = 'git@gitlab.com:acdc_epita/moulette/camltracer.git'
CAMLTRACER_RELEASE_TAG = '2021-release-1'
CAMLTRACER_LOCAL_DIR = os.path.join(MOULINETTE_FOLDER, 'camltracer')
CAMLTRACER_SETUP_PATCH_FILE = os.path.join(RES_FOLDER, 'camltracer-setup.patch')

TRISH_INSTALL_CMD = 'pip3 install git+ssh://git@gitlab.com/acdc_epita/moulette/trish.git'

EXIT_SUCCESS = 0
EXIT_FAILURE = 1 # external cause
EXIT_UNEXPECTED = 2 # bad user input/internal error/bug
