import os

ACDC_YEAR = 2021
SUP_YEAR = ACDC_YEAR + 2

ACDC_LOCAL_FOLDER = os.path.expanduser("~/.acdc")

TOOLKIT_FOLDER = os.path.dirname(os.path.dirname(__file__))

MOULINETTE_FOLDER = os.path.join(ACDC_LOCAL_FOLDER, "moulinettes")
STUDENTS_FOLDER = os.path.join(ACDC_LOCAL_FOLDER, "students")

DEFAULT_LOGINS_FILE = os.path.join(ACDC_LOCAL_FOLDER, "logins.txt")

REPO_FOLDER = "{tp_slug}-{login}"
REPO_URL = "git@git.cri.epita.fr:p/" + str(SUP_YEAR) + "-sup-tp/" + REPO_FOLDER
SUBMISSION_TAG = "submission"

MOULINETTE_REPO = "git@gitlab.com:acdc_epita/" + str(ACDC_YEAR) + "/{tp_slug}.git"
