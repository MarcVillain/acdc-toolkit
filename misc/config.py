import os

ACDC_YEAR = 2022
SUP_YEAR = ACDC_YEAR + 2
SEMESTER = 's1'

TOOLKIT_FOLDER = os.path.dirname(os.path.dirname(__file__))
RES_FOLDER = os.path.join(TOOLKIT_FOLDER, 'res')
ACDC_LOCAL_FOLDER = os.getenv('ACDC_DATA_DIR') or os.path.expanduser('@_DEFAULT_DATA_DIR_@')

MOULINETTE_FOLDER = os.path.join(ACDC_LOCAL_FOLDER, "moulinettes")
STUDENTS_FOLDER = os.path.join(ACDC_LOCAL_FOLDER, "students")
CORRECTIONS_FOLDER = os.path.join(ACDC_LOCAL_FOLDER, "corrections")

DEFAULT_LOGINS_FILE = os.path.join(ACDC_LOCAL_FOLDER, "logins.txt")

HISTORY_FILE = os.path.join(ACDC_LOCAL_FOLDER, ".toolkit_history")
HISTORY_SIZE = 1000
CORRECTION_HISTORY_FILE = os.path.join(ACDC_LOCAL_FOLDER, ".correction_history")

REPO_FOLDER = "{tp_slug}-{login}"
REPO_URL = "git@git.cri.epita.fr:p/" + str(SUP_YEAR) + "-" + SEMESTER + "-tp/" + REPO_FOLDER
SUBMISSION_TAG = "submission"

MOULINETTE_REPO = "git@gitlab.com:acdc_epita/" + str(ACDC_YEAR) + "/{tp_slug}.git"

CAMLTRACER_REPO = 'git@gitlab.com:acdc_epita/moulette/camltracer.git'
CAMLTRACER_COMMIT = '47ebbc0c171b55805f28e69148cd5af44bfc2b5b'
CAMLTRACER_LOCAL_DIR = os.path.join(MOULINETTE_FOLDER, 'camltracer')
CAMLTRACER_SETUP_PATCH_FILE = os.path.join(RES_FOLDER, 'camltracer-setup.patch')

TRISH_REPO = 'git@gitlab.com:acdc_epita/moulette/trish.git'
TRISH_COMMIT = '6b4058efa9f2902f242224182e1977a8697849c9'
TRISH_LOCAL_DIR = os.path.join(MOULINETTE_FOLDER, 'trish')

EXIT_SUCCESS = 0
EXIT_FAILURE = 1 # external cause
EXIT_UNEXPECTED = 2 # bad user input/internal error/bug
