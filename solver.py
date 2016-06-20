import sqlite3

from const import *
from pyraminx import Pyraminx


class PyraminxSolver(object):

    def __init__(self, pyraminx, path):
        self.pyraminx = pyraminx
        self.db = sqlite3.connect(path)

    def solve(self):
        print self.get_solution_from_state(self.pyraminx)

    def get_solution_from_state(self, state):
        c = self.db.cursor()

        q = [[state, '']]
        while True:
            c.execute('select solution from solutions where state = ?', [q[0][0].serialize_state()])
            solution = c.fetchone()
            if solution is not None:
                return q[0][1] + solution[0]

            for m in [('w', POS), ('w', NEG), ('x', POS), ('x', NEG), ('y', POS), ('y', NEG), ('z', POS), ('z', NEG)]:
                p = q[0][0].copy()
                getattr(p, 'rotate_' + m[0])(m[1])
                q.append([p, q[0][1] + m[0] + m[1]])

if __name__ == "__main__":
    p = Pyraminx()
    p.init_solved_state()
    p.rotate_w(POS)
    p.rotate_x(NEG)
    p.rotate_w(NEG)
    p.rotate_y(POS)

    print str(p)
    print p.serialize_state()

    s = PyraminxSolver(p, 'solutions.db')
    s.solve()
