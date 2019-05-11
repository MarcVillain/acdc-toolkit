from xml.etree import cElementTree

from commands.correct_actions.clear_files import ClearFiles
from commands.correct_actions.exit import Exit
from commands.correct_actions.next import Next
from commands.correct_actions.previous import Previous
from commands.correct_actions.copy_files import CopyFiles
from commands.correct_actions.shell import Shell
from commands.get import cmd_get
from misc.config import *
from misc.helpers import *
from misc.printer import *
from getkey import platform, keys

actions = [
    Previous(),
    Next(),
    Shell(),
    ClearFiles(),
    CopyFiles(),
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
    out={}
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
                solution_index, solutions, solutions_paths):
    for action in actions:
        if action.should_run(key):
            res = action.run(logins[login_index], logins_paths[login_index],
                             solutions[solution_index], solutions_paths[solution_index])
            if res is not None:
                solution_index += res
                while solution_index >= len(solutions):
                    solution_index -= len(solutions)
                    login_index += 1
                while solution_index < 0:
                    solution_index += len(solutions)
                    login_index -= 1
                login_index %= len(logins)

    return login_index, solution_index


def run_moulinette(no_rider, logins, tp_slug):
    logins_paths = [os.path.join(STUDENTS_FOLDER, tp_slug, REPO_FOLDER.format(tp_slug=tp_slug, login=login))
                    for login in logins]
    solutions_paths = [path
                       for path in folder_ls(os.path.join(MOULINETTE_FOLDER, tp_slug), excludes=["\\.git", ".*Tests.*"])
                       if os.path.isdir(path)]
    solutions = [os.path.basename(path) for path in solutions_paths]
    run_platform = platform(interrupts={})

    login_index, solution_index = run_actions(None, 0, logins, logins_paths, 0, solutions, solutions_paths)

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
        print_success("Student " + logins[login_index] + " (" + solutions[solution_index] + ") loaded")
        print_warning(actions_info_message)

        key = run_platform.getkey()
        if key == keys.CTRL_D:
            break

        login_index, solution_index = run_actions(key, login_index, logins, logins_paths,
                                                  solution_index, solutions, solutions_paths)


def cmd_correct(tp_slug, no_rider, logins):
    """
    Start the correction tool
    :param tp_slug: Slug of the TP to correct
    :param no_rider: Should we open rider or not
    :param logins: List of student logins
    """
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


def cplt_correct(text, line, begidx, endidx, options):
    return autocomplete(text, line, begidx, endidx,
                 [[folder for folder in folder_ls(STUDENTS_FOLDER)
                          if 'tp' in folder]],
                 options)

