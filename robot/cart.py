from ev3dev.auto import Motor, TouchSensor
from time import sleep

from const import *
from robot.common import *


class PyraminxCart:
    def __init__(self, drv_address, rot_address, zero_address):
        self.rot = Motor(rot_address)
        self.drv = Motor(drv_address)
        self.zero = TouchSensor(zero_address)
        self.current_pos = CART_POS_UNKNOWN

        assert self.rot.connected, 'Please connect a large cart.rot motor on %s' % rot_address
        assert self.drv.connected, 'Please connect a large cart.drv motor on %s' % drv_address
        assert self.zero.connected, 'Please connect a cart.zero touch sensor on %s' % zero_address

        self.drv_speed = -self.drv.max_speed
        self.rot_speed = self.rot.max_speed / 2

    def reset_drv(self):
        self.drv.reset()
        self.drv.run_forever(speed_sp=-200)
        self.drv.wait_until(Motor.STATE_STALLED)
        self.drv.stop(stop_action=HOLD)

        self.current_pos = CART_POS_A

    def reset_rot(self):
        self.rot.reset()
        self.rot.run_forever(speed_sp=100)
        while not self.zero.is_pressed:
            pass
        while self.zero.is_pressed:
            pass
        self.rot.run_forever(speed_sp=-100)
        while not self.zero.is_pressed:
            pass
        self.rot.stop(stop_action=HOLD)

    def relax(self):
        self.rot.stop(stop_action=COAST)
        self.drv.stop(stop_action=COAST)

    def cart_rot(self, direction):
        if direction == POS:
            run_for_degrees(self.rot, self.rot_speed, 90)
            self.rot.run_forever(speed_sp=200)

        if direction == NEG:
            run_for_degrees(self.rot, -self.rot_speed, 90)
            self.rot.run_forever(speed_sp=-200)

        while not self.zero.is_pressed:
            pass
        self.rot.stop(stop_action=HOLD)

    def cart_drv(self, destination):
        if self.current_pos == CART_POS_UNKNOWN:
            raise Exception('Unknown cart position, please reset before use')

        if destination == self.current_pos:
            return

        if self.current_pos == CART_POS_A and destination == CART_POS_B:
            run_for_degrees(self.drv, -self.drv_speed, 240, HOLD)
        if self.current_pos == CART_POS_A and destination == CART_POS_C:
            run_for_degrees(self.drv, -self.drv_speed, 760, HOLD)
        if self.current_pos == CART_POS_A and destination == CART_POS_E:
            run_for_degrees(self.drv, -self.drv_speed, 1080)

        if self.current_pos == CART_POS_B and destination == CART_POS_C:
            run_for_degrees(self.drv, -self.drv_speed, 180, HOLD)
        if self.current_pos == CART_POS_B and destination == CART_POS_E:
            run_for_degrees(self.drv, -self.drv_speed, 270)

        if self.current_pos == CART_POS_C and destination == CART_POS_A:
            run_for_degrees(self.drv, self.drv_speed, 600)
        if self.current_pos == CART_POS_C and destination == CART_POS_B:
            run_for_degrees(self.drv, self.drv_speed, 180, HOLD)
        if self.current_pos == CART_POS_C and destination == CART_POS_E:
            run_for_degrees(self.drv, -self.drv_speed, 480)

        if self.current_pos == CART_POS_E and destination == CART_POS_A:
            run_for_degrees(self.drv, self.drv_speed, 1080)
        if self.current_pos == CART_POS_E and destination == CART_POS_B:
            run_for_degrees(self.drv, self.drv_speed, 450, HOLD)
        if self.current_pos == CART_POS_E and destination == CART_POS_C:
            run_for_degrees(self.drv, self.drv_speed, 580, HOLD)
        if self.current_pos == CART_POS_E and destination == CART_POS_D:
            run_for_degrees(self.drv, self.drv_speed, 270, HOLD)

        # Approach the end stops
        if destination == CART_POS_A:
            run_until_stalled(self.drv, -200, HOLD)
        if destination == CART_POS_E:
            run_until_stalled(self.drv, 200, HOLD)

        self.current_pos = destination

    def rotate_w(self, direction, tip_only=False):
        if tip_only:
            self.cart_drv(CART_POS_B)
        else:
            self.cart_drv(CART_POS_A)

        self.cart_rot(direction)
        self.cart_drv(CART_POS_C)

    def turn_w(self, direction):
        self.cart_drv(CART_POS_C)
        self.cart_rot(direction)
