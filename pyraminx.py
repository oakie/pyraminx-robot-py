#!./run.sh /usr/bin/env python3

from const import *


def shift(tri, direction):
    if direction is POS:
        return tri[-1:] + tri[:-1]
    return tri[1:] + tri[:1]


class Polyhedron(object):
    def __init__(self, w=UNDEFINED, x=UNDEFINED, y=UNDEFINED, z=UNDEFINED):
        self.w = w
        self.x = x
        self.y = y
        self.z = z

    def copy(self):
        return Polyhedron(self.w, self.x, self.y, self.z)

    def get_colors(self):
        return [c for c in [self.w, self.x, self.y, self.z] if c is not None]

    def get_missing_colors(self):
        return list({GREEN, BLUE, YELLOW, ORANGE} - set(self.get_colors()))

    def set(self, face, color):
        setattr(self, face, color)

    def rotate_w(self, direction):
        self.x, self.z, self.y = shift([self.x, self.z, self.y], direction)

    def rotate_x(self, direction):
        self.w, self.y, self.z = shift([self.w, self.y, self.z], direction)

    def rotate_y(self, direction):
        self.w, self.z, self.x = shift([self.w, self.z, self.x], direction)

    def rotate_z(self, direction):
        self.w, self.x, self.y = shift([self.w, self.x, self.y], direction)

    def __str__(self):
        return '[' + str(self.w) + str(self.x) + str(self.y) + str(self.z) + ']'


class Pyraminx(object):
    def __init__(self):
        self.p = [None] * 3  # type: list[list[list[list[Polyhedron]]]]
        for w in range(0, 3):
            self.p[w] = [None] * 3
            for x in range(0, 3):
                self.p[w][x] = [None] * 3
                for y in range(0, 3):
                    self.p[w][x][y] = [None] * 3
                    for z in range(0, 3):
                        self.p[w][x][y][z] = Polyhedron()

    def copy(self):
        c = Pyraminx()
        for w in range(0, 3):
            for x in range(0, 3):
                for y in range(0, 3):
                    for z in range(0, 3):
                        if self.p[w][x][y][z] is not None:
                            c.p[w][x][y][z] = self.p[w][x][y][z].copy()
        return c

    def init_solved_state(self):
        # Tips
        self.p[2][0][0][0] = Polyhedron(UNDEFINED, BLUE, ORANGE, GREEN)
        self.p[0][2][0][0] = Polyhedron(YELLOW, UNDEFINED, ORANGE, GREEN)
        self.p[0][0][2][0] = Polyhedron(YELLOW, BLUE, UNDEFINED, GREEN)
        self.p[0][0][0][2] = Polyhedron(YELLOW, BLUE, ORANGE, UNDEFINED)

        # Centers
        self.p[1][0][0][0] = Polyhedron(UNDEFINED, BLUE, ORANGE, GREEN)
        self.p[0][1][0][0] = Polyhedron(YELLOW, UNDEFINED, ORANGE, GREEN)
        self.p[0][0][1][0] = Polyhedron(YELLOW, BLUE, UNDEFINED, GREEN)
        self.p[0][0][0][1] = Polyhedron(YELLOW, BLUE, ORANGE, UNDEFINED)

        # Edges
        self.p[1][1][0][0] = Polyhedron(UNDEFINED, UNDEFINED, ORANGE, GREEN)
        self.p[1][0][1][0] = Polyhedron(UNDEFINED, BLUE, UNDEFINED, GREEN)
        self.p[1][0][0][1] = Polyhedron(UNDEFINED, BLUE, ORANGE, UNDEFINED)
        self.p[0][1][1][0] = Polyhedron(YELLOW, UNDEFINED, UNDEFINED, GREEN)
        self.p[0][1][0][1] = Polyhedron(YELLOW, UNDEFINED, ORANGE, UNDEFINED)
        self.p[0][0][1][1] = Polyhedron(YELLOW, BLUE, UNDEFINED, UNDEFINED)

    def set_bottom_face(self, colors):
        self.p[0][0][0][2].set(W, colors[0])
        self.p[0][0][1][1].set(W, colors[1])
        self.p[0][0][0][1].set(W, colors[2])
        self.p[0][1][0][1].set(W, colors[3])
        self.p[0][0][2][0].set(W, colors[4])
        self.p[0][0][1][0].set(W, colors[5])
        self.p[0][1][1][0].set(W, colors[6])
        self.p[0][1][0][0].set(W, colors[7])
        self.p[0][2][0][0].set(W, colors[8])

    def __getitem__(self, item):
        return self.p[item[0]][item[1]][item[2]][item[3]]

    def __setitem__(self, key, value):
        self.p[key[0]][key[1]][key[2]][key[3]] = value

    def rotate_w(self, direction, tip_only=False):
        self.p[2][0][0][0].rotate_w(direction)
        if tip_only:
            return

        self.p[1][0][0][0].rotate_w(direction)
        self.p[1][1][0][0].rotate_w(direction)
        self.p[1][0][1][0].rotate_w(direction)
        self.p[1][0][0][1].rotate_w(direction)
        self.swap((1, 1, 0, 0), (1, 0, 0, 1), (1, 0, 1, 0), direction)

    def rotate_x(self, direction, tip_only=False):
        self.p[0][2][0][0].rotate_x(direction)
        if tip_only:
            return

        self.p[0][1][0][0].rotate_x(direction)
        self.p[1][1][0][0].rotate_x(direction)
        self.p[0][1][1][0].rotate_x(direction)
        self.p[0][1][0][1].rotate_x(direction)
        self.swap((1, 1, 0, 0), (0, 1, 1, 0), (0, 1, 0, 1), direction)

    def rotate_y(self, direction, tip_only=False):
        self.p[0][0][2][0].rotate_y(direction)
        if tip_only:
            return

        self.p[0][0][1][0].rotate_y(direction)
        self.p[1][0][1][0].rotate_y(direction)
        self.p[0][1][1][0].rotate_y(direction)
        self.p[0][0][1][1].rotate_y(direction)
        self.swap((1, 0, 1, 0), (0, 0, 1, 1), (0, 1, 1, 0), direction)

    def rotate_z(self, direction, tip_only=False):
        self.p[0][0][0][2].rotate_z(direction)
        if tip_only:
            return

        self.p[0][0][0][1].rotate_z(direction)
        self.p[1][0][0][1].rotate_z(direction)
        self.p[0][1][0][1].rotate_z(direction)
        self.p[0][0][1][1].rotate_z(direction)
        self.swap((1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1), direction)

    def swap(self, a, b, c, direction):
        if direction is POS:
            self[a], self[b], self[c] = self[c], self[a], self[b]
        else:
            self[a], self[b], self[c] = self[b], self[c], self[a]

    def turn_w(self, direction):
        self.rotate_w(direction)
        for x in range(0, 3):
            for y in range(0, 3):
                for z in range(0, 3):
                    if self.p[0][x][y][z] is not None:
                        self.p[0][x][y][z].rotate_w(direction)
        self.swap((0, 2, 0, 0), (0, 0, 0, 2), (0, 0, 2, 0), direction)
        self.swap((0, 1, 0, 0), (0, 0, 0, 1), (0, 0, 1, 0), direction)
        self.swap((0, 1, 1, 0), (0, 1, 0, 1), (0, 0, 1, 1), direction)

    def turn_x(self, direction):
        self.rotate_x(direction)
        for w in range(0, 3):
            for y in range(0, 3):
                for z in range(0, 3):
                    if self.p[w][0][y][z] is not None:
                        self.p[w][0][y][z].rotate_x(direction)
        self.swap((2, 0, 0, 0), (0, 0, 2, 0), (0, 0, 0, 2), direction)
        self.swap((1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1), direction)
        self.swap((1, 0, 1, 0), (0, 0, 1, 1), (1, 0, 0, 1), direction)

    def turn_y(self, direction):
        self.rotate_y(direction)
        for w in range(0, 3):
            for x in range(0, 3):
                for z in range(0, 3):
                    if self.p[w][x][0][z] is not None:
                        self.p[w][x][0][z].rotate_y(direction)
        self.swap((2, 0, 0, 0), (0, 0, 0, 2), (0, 2, 0, 0), direction)
        self.swap((1, 0, 0, 0), (0, 0, 0, 1), (0, 1, 0, 0), direction)
        self.swap((1, 1, 0, 0), (1, 0, 0, 1), (0, 1, 0, 1), direction)

    def turn_z(self, direction):
        self.rotate_z(direction)
        for w in range(0, 3):
            for x in range(0, 3):
                for y in range(0, 3):
                    if self.p[w][x][y][0] is not None:
                        self.p[w][x][y][0].rotate_z(direction)
        self.swap((2, 0, 0, 0), (0, 2, 0, 0), (0, 0, 2, 0), direction)
        self.swap((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), direction)
        self.swap((1, 1, 0, 0), (0, 1, 1, 0), (1, 0, 1, 0), direction)

    def process_rotations(self, moves, tips_only=False):
        for axis, direction in zip(moves[0::2], moves[1::2]):
            getattr(self, 'rotate_' + axis)(direction, tips_only)

    def process_turns(self, moves):
        for axis, direction in zip(moves[0::2], moves[1::2]):
            getattr(self, 'turn_' + axis)(direction)

    def get_tip_alignment(self, axis):
        axial, tip = self[axial_map[axis][1]], self[axial_map[axis][2]]
        faces = axial_offset[axis]
        if getattr(tip, faces[1]) == getattr(axial, faces[0]):
            return POS
        if getattr(tip, faces[1]) == getattr(axial, faces[2]):
            return NEG
        return None

    def get_transform(self):
        tip_w = face_color_map[self[(2, 0, 0, 0)].get_missing_colors()[0]]
        tip_x = face_color_map[self[(0, 2, 0, 0)].get_missing_colors()[0]]
        return tip_w, tip_x

    def get_tips(self):
        tip_w = face_color_map[self[(2, 0, 0, 0)].get_missing_colors()[0]]
        tip_x = face_color_map[self[(0, 2, 0, 0)].get_missing_colors()[0]]
        tip_y = face_color_map[self[(0, 0, 2, 0)].get_missing_colors()[0]]
        tip_z = face_color_map[self[(0, 0, 0, 2)].get_missing_colors()[0]]
        return tip_w, tip_x, tip_y, tip_z

    def serialize_state(self):
        ser = ''
        # Centers
        ser += str(self.p[1][0][0][0])
        ser += str(self.p[0][1][0][0])
        ser += str(self.p[0][0][1][0])
        ser += str(self.p[0][0][0][1])

        # Edges
        ser += str(self.p[1][1][0][0])
        ser += str(self.p[1][0][1][0])
        ser += str(self.p[1][0][0][1])
        ser += str(self.p[0][1][1][0])
        ser += str(self.p[0][1][0][1])
        ser += str(self.p[0][0][1][1])

        return ser

    def __str__(self):
        s = '  '
        s += self[(2, 0, 0, 0)].y + '     '
        s += self[(2, 0, 0, 0)].z + '     '
        s += self[(2, 0, 0, 0)].x + '\n'

        s += ' '
        s += self[(1, 0, 0, 1)].y + self[(1, 0, 0, 0)].y + self[(1, 1, 0, 0)].y + '   '
        s += self[(1, 1, 0, 0)].z + self[(1, 0, 0, 0)].z + self[(1, 0, 1, 0)].z + '   '
        s += self[(1, 0, 1, 0)].x + self[(1, 0, 0, 0)].x + self[(1, 0, 0, 1)].x + '\n'

        s += self[(0, 0, 0, 2)].y + self[(0, 0, 0, 1)].y + self[(0, 1, 0, 1)].y + self[(0, 1, 0, 0)].y + self[(0, 2, 0, 0)].y + ' '
        s += self[(0, 2, 0, 0)].z + self[(0, 1, 0, 0)].z + self[(0, 1, 1, 0)].z + self[(0, 0, 1, 0)].z + self[(0, 0, 2, 0)].z + ' '
        s += self[(0, 0, 2, 0)].x + self[(0, 0, 1, 0)].x + self[(0, 0, 1, 1)].x + self[(0, 0, 0, 1)].x + self[(0, 0, 0, 2)].x + '\n'

        s += '      ' + self[(0, 2, 0, 0)].w + self[(0, 1, 0, 0)].w + self[(0, 1, 1, 0)].w + self[(0, 0, 1, 0)].w + self[(0, 0, 2, 0)].w + '\n'
        s += '       ' + self[(0, 1, 0, 1)].w + self[(0, 0, 0, 1)].w + self[(0, 0, 1, 1)].w + '\n'
        s += '        ' + self[(0, 0, 0, 2)].w

        return s
