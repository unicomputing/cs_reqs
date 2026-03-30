from collections import namedtuple
from pprint import pprint
from ortools_version.course_catalog import catalog

# ── Full degree (all requirements satisfied) ─────────────────────────────────
# PHY 132 added vs ref tests so science reaches 9 credits:
#   PHY 131(3) + PHY 133(1) + PHY 132(3) + AST 203(3) = 10

_FULL = {
    'CSE 114', 'CSE 214', 'CSE 216', 'CSE 215', 'CSE 220',            # intro
    'CSE 303', 'CSE 310', 'CSE 316', 'CSE 320', 'CSE 373', 'CSE 416', # adv
    'CSE 360', 'CSE 361', 'CSE 351', 'CSE 352', 'CSE 353', 'CSE 355', # elect
    'MAT 131', 'MAT 132', 'AMS 210', 'AMS 301', 'AMS 310',            # math
    'PHY 131', 'PHY 132', 'PHY 133', 'AST 203',                        # science
    'CSE 300', 'CSE 312',                                               # ethics+writing
}

Taken = namedtuple('Taken', ['id', 'credits', 'grade', 'when', 'where'])

def test_check_full():
    """Full course set — all requirements satisfied."""
    taken = {Taken(cid, catalog[cid].credits, 'A', (2024, 2), 'SB') for cid in _FULL}
    checked = {req: (True, []) for req in
               ['intro', 'adv', 'elect', 'calc', 'alg', 'sta', 'sci',
                'ethics', 'writing', 'credits_at_SB', 'degree']}
    return taken, checked

if __name__ == '__main__':
    import inspect, sys
    this = sys.modules[__name__]
    for name, func in sorted(inspect.getmembers(this, inspect.isfunction)):
        if name.startswith('test_'):
            taken, checked = func()
            print(f'---- {name}')
            print(f'     taken_ids: {sorted({c.id for c in taken})}')
            pprint(checked)
            print()