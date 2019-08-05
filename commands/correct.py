import os
from xml.etree import cElementTree

from commands.correct_actions.all_public import AllPublic
from commands.correct_actions.build import Build
from commands.correct_actions.clear_files import ClearFiles
from commands.correct_actions.exit import Exit
from commands.correct_actions.log import Log
from commands.correct_actions.next import Next
from commands.correct_actions.previous import Previous
from commands.correct_actions.copy_files import CopyFiles
from commands.correct_actions.readme import Readme
from commands.correct_actions.refresh import Refresh
from commands.correct_actions.shell import Shell
from commands.correct_actions.tree import Tree
from commands.get import cmd_get
from getkey import platform, keys

from helpers.autocomplete import CmdCompletor, enum_files, enum_tp_slugs, enum_logins_for_tp
from helpers.command import exec_in_folder
from helpers.git import git_clone
from helpers.io import folder_ls, folder_find, folder_exists, folder_create
from helpers.terminal import open_rider
from misc.config import MOULINETTE_REPO, STUDENTS_FOLDER, MOULINETTE_FOLDER, REPO_FOLDER, EXIT_SUCCESS
from misc.printer import print_info, print_success, print_press_enter, print_warning, print_error
from misc.data import Tp, Submission


actions = [
    Previous(),
    Next(),
    Refresh(),
    Build(),
    Shell(),
    ClearFiles(),
    CopyFiles(),
    AllPublic(),
    Log(),
    Tree(),
    Readme(),
    Exit(),
]


def download_moulinette(tp_slug):
    print_info("Downloading moulinette")
    git_clone(MOULINETTE_REPO.format(tp_slug=tp_slug))
    print_success("Download successful")


def __parse_tests(xml, out):
    for test in xml.findall('test-case'):
        result = test.get('result').lower()
        out['tests'].append({
            'name': test.get('fullname'),
            'result': result,
            'duration': round(float(test.get('duration')) * 1000, 3),
            'asserts': test.get('asserts')
        })
        out['stats']['total'] += 1
        if result in out['stats']:
            out['stats'][result] += 1
        else:
            out['stats'][result] = 1
    for test in xml.findall('test-suite'):
        __parse_tests(test, out)


def parse_tests(path):
    root = cElementTree.parse(path).getroot()
    out = {}
    out['stats'] = {}
    out['stats']['passed'] = 0
    out['stats']['failed'] = 0
    out['stats']['total'] = 0
    out['tests'] = []
    __parse_tests(root, out)
    return out


def create_actions_info_message():
    def boldify(message):
        elts = message.split(":")
        return "\033[1m" + elts[0] + "\033[21m:" + elts[1]

    return ', '.join(boldify(str(action))
                     for action in actions
                     if str(action))


def run_actions(key, login_index, logins, logins_paths,
                project_index, projects, projects_paths):
    student_folder_exists = folder_exists(logins_paths[login_index])
    for action in actions:
        if action.should_run(key) \
                and (student_folder_exists or not action.requires_student_folder()):
            res = action.run(logins[login_index], logins_paths[login_index],
                             projects[project_index], projects_paths[project_index])
            if res is not None:
                project_index += res
                while project_index >= len(projects):
                    project_index -= len(projects)
                    login_index += 1
                while project_index < 0:
                    project_index += len(projects)
                    login_index -= 1
                login_index %= len(logins)
                # Add space in display when looping back on logins
                if login_index == 0 and project_index == 0:
                    print("\n")
        student_folder_exists = folder_exists(logins_paths[login_index])

    return login_index, project_index


def run_moulinette(no_rider, logins, tp_slug):
    csproj_paths = [path
                    for path in
                    folder_find(os.path.join(MOULINETTE_FOLDER, tp_slug),
                                includes=[".*\\.csproj"],
                                excludes=["\\..*", ".*Tests.*", ".*Correction.*"], depth=3)
                    if path.endswith(".csproj")]

    projects_paths = sorted(list({os.path.dirname(path) for path in csproj_paths}))
    solutions_paths = list({os.path.dirname(path) for path in projects_paths})

    solutions = [os.path.basename(path) for path in solutions_paths]
    projects = [os.path.join(os.path.basename(os.path.dirname(path)), os.path.basename(path))
                for path in projects_paths]

    logins_paths = [os.path.join(STUDENTS_FOLDER, tp_slug, REPO_FOLDER.format(tp_slug=tp_slug, login=login))
                    for login in logins]

    run_platform = platform(interrupts={})

    login_index, project_index = run_actions(None, 0, logins, logins_paths, 0, projects, projects_paths)

    actions_info_message = create_actions_info_message()

    if not no_rider:
        if len(solutions_paths) > 1:
            print_info("Opening rider windows")
            print_warning("Click on 'New Window'")
        else:
            print_info("Opening rider window")

        for solution_path in solutions_paths:
            open_rider(solution_path)

        if len(solutions_paths) > 1:
            print_press_enter("when the windows are opened")
        else:
            print_press_enter("when the window is opened")

    while True:
        msg = "Student " + logins[login_index] + " (" + projects[project_index] + ")"
        if not folder_exists(logins_paths[login_index]):
            print_error(msg + " not found")
        else:
            print_success(msg + " loaded")
        print_warning(actions_info_message)

        key = run_platform.getkey()
        if key == keys.CTRL_D:
            break

        login_index, project_index = run_actions(key, login_index, logins, logins_paths,
                                                 project_index, projects, projects_paths)


def cmd_correct(tp_slug, no_rider, logins, get_rendus):
    """
    Start the correction tool
    :param tp_slug: Slug of the TP to correct
    :param no_rider: Should we open rider or not
    :param logins: List of student logins
    :param get_rendus: Should we call get before correct?
    """
    if get_rendus:
        cmd_get(tp_slug, logins)

    if not folder_exists(MOULINETTE_FOLDER):
        folder_create(MOULINETTE_FOLDER)

    tp_folder = os.path.join(MOULINETTE_FOLDER, tp_slug)

    if not folder_exists(tp_folder):
        exec_in_folder(MOULINETTE_FOLDER,
                       download_moulinette,
                       tp_slug)

    exec_in_folder(tp_folder,
                   run_moulinette,
                   no_rider, logins, tp_slug)

    return EXIT_SUCCESS


CPLT = CmdCompletor(
    [ '-g', '--get', '--no-rider' ],
    { '--file=': enum_files },
    [ enum_tp_slugs, enum_logins_for_tp ])

def cplt_correct(text, line, begidx, endidx):
    return CPLT.complete(text, line, begidx, endidx)
