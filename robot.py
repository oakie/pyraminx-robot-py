

from const import *
from pyraminx import Pyraminx
from scanner import PyraminxScanner
from solver import PyraminxSolver

# from ev3dev.auto import *
#
# class PyraminxRobot(object):
#     def __init__(self):
#         self.cart_drive = LargeMotor('outA')
#         self.cart_turn = LargeMotor('outB')
#         self.claw_grip = MediumMotor('outC')
#         self.claw_turn = LargeMotor('outD')
#
#         self.verify_motors()
#         self.cart_turn.run_timed(time_sp=2000, speed_sp=100)
#
#     def verify_motors(self):
#         assert self.cart_drive.connected, 'Please connect a large cart drive motor on port A'
#         assert self.cart_turn.connected, 'Please connect a large cart turn motor on port B'
#         assert self.claw_grip.connected, 'Please connect a medium claw grip motor on port C'
#         assert self.claw_turn.connected, 'Please connect a large claw turn motor on port D'

if __name__ == "__main__":
    pyraminx = Pyraminx()
    # robot = PyraminxRobot()
    scanner = PyraminxScanner('http://192.168.0.17/')
    solver = PyraminxSolver(pyraminx, 'solutions.db')

    # calibrate robot

    # wait to receive pyraminx

    # calibrate camera
    scanner.calibrate()

    # wait for start signal

    # --- scan face by face ---
    colors = scanner.scan_face()
    pyraminx.set_bottom_face(colors)

    # robot.turn_z(POS)
    pyraminx.turn_z(POS)
    colors = scanner.scan_face()
    pyraminx.set_bottom_face(colors)

    # robot.turn_z(POS)
    pyraminx.turn_z(POS)
    colors = scanner.scan_face()
    pyraminx.set_bottom_face(colors)

    # robot.turn_w(NEG)
    # robot.turn_z(NEG)
    pyraminx.turn_w(NEG)
    pyraminx.turn_z(NEG)
    colors = scanner.scan_face()
    pyraminx.set_bottom_face(colors)

    print str(pyraminx)
    # --- --- --- --- --- --- ---

    # search for solution

    # solve pyraminx
