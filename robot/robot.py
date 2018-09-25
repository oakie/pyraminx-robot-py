#!./run.sh /usr/bin/env python3

from ev3dev.auto import TouchSensor, Motor

from const import *

from robot.tool import PyraminxTool
from robot.cart import PyraminxCart


class PyraminxRobot(object):
    def __init__(self):
        self.cart = PyraminxCart(drv_address='outA', rot_address='outB', zero_address='in1')
        self.tool = PyraminxTool(act_address='outD', rot_address='outC', zkey_address='in4', zrot_address='in2')

    def reset(self):
        self.cart.reset_drv()
        self.cart.reset_rot()

        self.tool.reset_key()

        self.tool.reset_rot()
        self.cart.cart_drv(CART_POS_E)
        self.tool.reset_grp()

        self.cart.cart_drv(CART_POS_C)

    def soft_reset(self):
        self.cart.current_pos = CART_POS_C
        self.tool.current_grp = TOOL_GRP_OPEN
        self.tool.current_key = TOOL_KEY_OPEN

    def relax(self):
        self.cart.relax()
        self.tool.relax()

    def execute(self, moves, tips=''):
        tips = [tips[i:i + 2] for i in range(0, len(tips), 2)]
        for axis, direction in zip(moves[0::2], moves[1::2]):
            print('exec ' + axis + ' ' + direction)
            if axis == W:
                self.twist(direction, tips, W)
            if axis == X:
                self.flip('z-')
                self.twist(direction, tips, X)
                self.flip('z+')
            if axis == Y:
                self.flip('z+')
                self.twist(direction, tips, Y)
                self.flip('z-')
            if axis == Z:
                self.cart.cart_drv(CART_POS_D)
                self.cart.cart_rot(POS)
                self.flip('z+')
                self.twist(direction, tips, Z)
                self.flip('z-')
                self.cart.cart_drv(CART_POS_D)
                self.cart.cart_rot(NEG)

        for axis, direction in [(t[0], t[1]) for t in tips]:
            print('tip ' + axis + ' ' + direction)
            if axis == W:
                self.twist_tip(direction)
            if axis == X:
                self.flip('z-')
                self.twist_tip(direction)
                self.flip('z+')
            if axis == Y:
                self.flip('z+')
                self.twist_tip(direction)
                self.flip('z-')
            if axis == Z:
                self.cart.cart_rot(POS)
                self.cart.cart_drv(CART_POS_D)
                self.flip('z-')
                self.twist_tip(direction)
                self.flip('z+')
                self.cart.cart_drv(CART_POS_D)
                self.cart.cart_rot(NEG)

    def check_tips(self, tips, tip):
        t = next((x for x in tips if x[0] is tip), None)
        if t is None:
            return
        self.twist_tip(t[1])
        tips.remove(t)

    def flip(self, moves):
        for axis, direction in zip(moves[0::2], moves[1::2]):
            if axis == W:
                self.cart.cart_rot(direction)

            if axis == Z:
                self.cart.cart_drv(CART_POS_E)
                self.tool.tool_grp(TOOL_GRP_SHUT)
                self.cart.cart_drv(CART_POS_D)
                self.tool.tool_rot(direction)
                self.cart.cart_drv(CART_POS_E)
                self.tool.tool_grp(TOOL_GRP_OPEN)

    def twist(self, direction, tips, tip_up):
        self.cart.cart_drv(CART_POS_A)
        self.tool.tool_key(TOOL_KEY_SHUT)
        self.cart.cart_rot(counter_rotation[direction])
        self.tool.tool_key(TOOL_KEY_OPEN)
        self.cart.cart_rot(direction)
        self.check_tips(tips, tip_up)
        self.cart.cart_drv(CART_POS_C)

    def twist_tip(self, direction):
        self.cart.cart_drv(CART_POS_A)
        self.cart.cart_drv(CART_POS_B)
        self.tool.tool_key(TOOL_KEY_SHUT)
        self.cart.cart_rot(counter_rotation[direction])
        self.tool.tool_key(TOOL_KEY_OPEN)
        self.cart.cart_rot(direction)
