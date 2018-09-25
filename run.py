#!./run.sh

from ev3dev.auto import Sound
from time import sleep

from const import *

from pyraminx import Pyraminx
from robot.robot import PyraminxRobot
# from scanner.scanner import AndroidScanner
from solver.solver import PyraminxSolver


def solve(pyraminx, robot, scanner, solver):
    Sound.speak('Solver starting').wait()
    robot.execute('z+')
    Sound.speak('Solver finished').wait()


def reset(robot):
    Sound.speak('Reset starting').wait()
    robot.reset()
    Sound.speak('Reset finished').wait()


if __name__ == "__main__":
    robot = PyraminxRobot()
    robot.cart.reset_drv()
    robot.cart.cart_drv(CART_POS_C)
    robot.soft_reset()

    sleep(3)
    robot.execute('x+', 'x+y+')

