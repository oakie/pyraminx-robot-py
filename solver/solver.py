import sqlite3

from const import *
from pyraminx import Pyraminx, Polyhedron


def transform_moves(moves, transform):
    poly = Polyhedron(YELLOW, BLUE, ORANGE, GREEN)
    for axis, direction in zip(transform[0::2], transform[1::2]):
        getattr(poly, 'rotate_' + axis)(direction)
    axis_map = {}
    for new_axis in [W, X, Y, Z]:
        old_axis = face_color_map[getattr(poly, new_axis)]
        axis_map[old_axis] = new_axis

    transformed_moves = ''
    for axis, direction in zip(moves[0::2], moves[1::2]):
        transformed_moves += axis_map[axis] + direction
    return transformed_moves


class PyraminxSolver(object):

    def __init__(self, pyraminx, path):
        self.pyraminx = pyraminx
        self.db = sqlite3.connect(path)

    def solve(self):
        return self.get_main_solution(), self.get_tip_solution()

    def get_main_solution(self):
        c = self.db.cursor()

        t = transform_map[self.pyraminx.get_transform()]
        transformed_state = self.pyraminx.copy()
        transformed_state.process_turns(t[0])
        print(str(transformed_state))

        q = [(transformed_state, '')]
        while len(q) > 0:
            c.execute('select solution from solutions where state = ?', [q[0][0].serialize_state()])
            solution = c.fetchone()
            if solution is not None:
                return transform_moves(q[0][1] + solution[0], t[1])

            for m in [('w', POS), ('w', NEG), ('x', POS), ('x', NEG), ('y', POS), ('y', NEG), ('z', POS), ('z', NEG)]:
                child_state = q[0][0].copy()
                getattr(child_state, 'rotate_' + m[0])(m[1])
                q.append((child_state, q[0][1] + m[0] + m[1]))
        return None

    def get_tip_solution(self):
        return [counter_rotation[self.pyraminx.get_tip_alignment(axis)] for axis in [W, X, Y, Z]]


if __name__ == "__main__":
    p = Pyraminx()
    p.init_solved_state()

    p.rotate_w(NEG)
    p.rotate_x(NEG)
    p.rotate_y(NEG)
    p.rotate_z(POS)

    p.turn_w(POS)

    print(str(p))
    print(p.serialize_state())

    s = PyraminxSolver(p, 'solutions.db')
    print(s.solve())
