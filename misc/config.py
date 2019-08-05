import os

ACDC_YEAR = 2021
SUP_YEAR = ACDC_YEAR + 2

TOOLKIT_FOLDER = os.path.dirname(os.path.dirname(__file__))
ACDC_LOCAL_FOLDER = os.path.expanduser('@_DATA_DIR_@')

MOULINETTE_FOLDER = os.path.join(ACDC_LOCAL_FOLDER, "moulinettes")
STUDENTS_FOLDER = os.path.join(ACDC_LOCAL_FOLDER, "students")

DEFAULT_LOGINS_FILE = os.path.join(ACDC_LOCAL_FOLDER, "logins.txt")

HISTORY_FILE = os.path.join(ACDC_LOCAL_FOLDER, ".toolkit_history")
HISTORY_SIZE = 1000

REPO_FOLDER = "{tp_slug}-{login}"
REPO_URL = "git@git.cri.epita.fr:p/" + str(SUP_YEAR) + "-sup-tp/" + REPO_FOLDER
SUBMISSION_TAG = "submission"

MOULINETTE_REPO = "git@gitlab.com:acdc_epita/" + str(ACDC_YEAR) + "/{tp_slug}.git"

EXIT_SUCCESS = 0
EXIT_FAILURE = 1 # external cause
EXIT_UNEXPECTED = 2 # bad user input/internal error/bug
