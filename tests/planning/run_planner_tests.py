import inspect
import io
import importlib
import re
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def collect_tests():
    modules = []
    for path in sorted(Path(__file__).parent.glob('planner_test_cases*.py')):
        module_name = f"tests.planning.{path.stem}"
        modules.append(importlib.import_module(module_name))

    tests = []
    for module in modules:
        module_tests = [
            (f"{module.__name__.split('.')[-1]}.{name}", func)
            for name, func in inspect.getmembers(module, inspect.isfunction)
            if name.startswith('test_plan_')
        ]
        tests.extend(sorted(module_tests))
    return tests


ALL_TESTS = collect_tests()


def normalize_witness(value):
    return re.sub(r" \(sem \d+\)$", "", value)


def normalize_checked(checked):
    out = {}
    for req, (ok, witness) in checked.items():
        out[req] = (ok, sorted({normalize_witness(w) for w in witness}))
    return out

def to_checker_taken(history, planned_courses):
    from ortools_version.planner import catalog
    from python_version.cs_reqs_2024 import Taken

    taken = set()
    for h in history:
        taken.add(Taken(h.id, h.credits, h.grade, h.when, h.where))
    for cid, when in planned_courses.items():
        taken.add(Taken(cid, catalog[cid].credits, 'C', when, 'SB'))
    return taken


def clingo_sem_to_when(sem):
    return 2024 + (sem - 1) // 4, ((sem - 1) % 4) + 1


def validate_with_checker(history, planned_courses):
    import python_version.cs_reqs_2024 as checker
    from python_version.cs_reqs_2024 import degree_reqs

    checker.w = {}
    with redirect_stdout(io.StringIO()):
        result = degree_reqs(to_checker_taken(history, planned_courses))
    return result, result['degree'][0]


def run_ortools(case):
    from ortools_version.course_catalog import Major, Standing
    from ortools_version.planner import plan_courses

    history, _ = case
    with redirect_stdout(io.StringIO()):
        checked, schedule, _ = plan_courses(history, Major('CSE'), Standing('U4'), schedule=True)
    checker_result, checker_ok = validate_with_checker(history, schedule)
    failed = [k for k, v in checker_result.items() if not v[0]]
    return normalize_checked(checked), set(schedule), schedule, checker_ok, failed


def run_clingo_backend(case):
    from clingo_version.run_clingo import run_clingo
    from python_version.cs_reqs_2024 import Taken

    history, _ = case
    taken = {
        Taken(h.id, h.credits, h.grade, h.when, h.where)
        for h in history
    }
    with redirect_stdout(io.StringIO()):
        checked, schedule, _ = run_clingo(
            taken_set=taken,
            mode='plan',
            main_lp=str(ROOT / 'clingo_version' / 'cse_req_clingo.lp'),
            kb_lp=str(ROOT / 'course_kb' / 'kb_complete.lp'),
        )

    planned_courses = {}
    for sem, courses in schedule.items():
        when = clingo_sem_to_when(sem)
        for cid in courses:
            planned_courses[cid] = when

    checker_result, checker_ok = validate_with_checker(history, planned_courses)
    failed = [k for k, v in checker_result.items() if not v[0]]
    schedule_courses = {cid for courses in schedule.values() for cid in courses}
    return normalize_checked(checked), schedule_courses, planned_courses, checker_ok, failed


def run_one(label, backend):
    passed = []
    failed = []

    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        for name, func in ALL_TESTS:
            try:
                case = func()
                checked, schedule_courses, schedule_by_course, checker_ok, checker_failed = backend(case)
                if not checker_ok:
                    failed.append((name, f"python checker rejected combined plan on: {checker_failed}"))
                    continue

                _, validate = case
                validate(checked, schedule_courses, schedule_by_course)
                passed.append(name)
            except Exception as e:
                failed.append((name, str(e)))

    print(f"\n-> {label}: passed {len(passed)} test cases, failed {len(failed)} test cases")
    for name, error in failed:
        print(f"   FAIL: {name}")
        print(f"      - {error}")


def run_all():
    run_one('ortools_version', run_ortools)
    run_one('clingo_version', run_clingo_backend)


if __name__ == '__main__':
    run_all()
