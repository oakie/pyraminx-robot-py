import sqlite3

from const import *
from pyraminx import Pyraminx


buffer = []


def save(conn, state, solution):
    global buffer
    buffer.append([state, solution])

    if len(buffer) == 100:
        c = conn.cursor()
        c.executemany('insert or ignore into solutions (state, solution) values (?, ?)', buffer)
        conn.commit()
        buffer = []


def increment(counter, idx):
    if idx == -1:
        counter[:0] = [1]
    else:
        counter[idx] += 1
        if counter[idx] == 8:
            counter[idx] = 0
            increment(counter, idx - 1)


def generate_solutions(db_conn):
    p = Pyraminx()
    move = [p.rotate_w, p.rotate_w, p.rotate_x, p.rotate_x, p.rotate_y, p.rotate_y, p.rotate_z, p.rotate_z]
    dirs = [POS, NEG, POS, NEG, POS, NEG, POS, NEG]
    abbr = [W, W, X, X, Y, Y, Z, Z]
    anti = [NEG, POS, NEG, POS, NEG, POS, NEG, POS]
    counter = [0]
    i = 0
    while len(counter) < 10:
        p.init_solved_state()
        for c in counter:
            move[c](dirs[c])
        state = p.serialize_state()

        solution = ''
        for c in reversed(counter):
            solution += abbr[c] + anti[c]

        # save(db_conn, state, solution)
        print(i)
        if state is '[.BOG][O.GY][BG.Y][YBO.][..OG][.Y.O][.BO.][B..Y][G.B.][YG..]':
            print(solution)

        increment(counter, len(counter) - 1)
        i += 1

if __name__ == "__main__":
    conn = sqlite3.connect('solutions.db')
    generate_solutions(conn)
    conn.close()
