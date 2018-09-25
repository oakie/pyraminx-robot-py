from ev3dev.auto import Motor, MediumMotor, TouchSensor, ColorSensor

from const import *
from robot.common import *


class PyraminxTool:
    def __init__(self, act_address, rot_address, zkey_address, zrot_address):
        self.grp = MediumMotor(act_address)
        self.key = MediumMotor(act_address)
        self.rot = Motor(rot_address)
        self.zkey = ColorSensor(zkey_address)
        self.zrot = TouchSensor(zrot_address)
        self.current_grp = TOOL_GRP_UNKNOWN
        self.current_key = TOOL_KEY_UNKNOWN

        assert self.grp.connected, 'Please connect a medium tool.grp motor on %s' % act_address
        assert self.key.connected, 'Please connect a medium tool.key motor on %s' % act_address
        assert self.rot.connected, 'Please connect a large tool.rot motor on %s' % rot_address
        assert self.zrot.connected, 'Please connect a tool.zrot touch sensor on %s' % zrot_address
        assert self.zkey.connected, 'Please connect a tool.zkey color sensor on %s' % zkey_address

        self.zkey.mode = 'COL-REFLECT'
        self.rot_ratio = 60 / 24
        self.rot_speed = self.rot.max_speed
        self.grp_speed = self.grp.max_speed
        self.key_speed = self.key.max_speed
        self.zkey_threshold = 50

    def reset_rot(self):
        self.rot.reset()
        self.rot.run_forever(speed_sp=100)
        while not self.zrot.is_pressed:
            pass
        while self.zrot.is_pressed:
            pass
        self.rot.run_forever(speed_sp=-100)
        while not self.zrot.is_pressed:
            pass
        self.rot.stop(stop_action=HOLD)

    def reset_grp(self):
        self.grp.reset()
        self.grp.run_timed(speed_sp=1000, stop_action=HOLD, time_sp=5000)
        self.grp.wait_while(Motor.STATE_RUNNING)
        self.current_grp = TOOL_GRP_OPEN

    def reset_key(self):
        self.key.reset()
        self.key.run_forever(speed_sp=self.key_speed)

        # Approach key photo cell stop
        while self.zkey.reflected_light_intensity < self.zkey_threshold:
            pass
        run_for_degrees(self.key, self.key_speed, 360, HOLD)

        self.current_key = TOOL_KEY_OPEN

    def relax(self):
        self.rot.stop(stop_action=COAST)
        self.grp.stop(stop_action=COAST)
        self.key.stop(stop_action=COAST)

    def tool_rot(self, direction):
        if direction == POS:
            run_for_degrees(self.rot, -self.rot_speed, self.rot_ratio * 90)
            self.rot.run_forever(speed_sp=-self.rot_speed / 2)

        if direction == NEG:
            run_for_degrees(self.rot, self.rot_speed, self.rot_ratio * 90)
            self.rot.run_forever(speed_sp=self.rot_speed / 2)

        # Approach rotation stop
        while not self.zrot.is_pressed:
            pass
        self.rot.stop(stop_action=HOLD)

    def tool_grp(self, state):
        if self.current_grp == TOOL_GRP_UNKNOWN:
            raise Exception('Unknown grp state, please reset before use')

        if state == TOOL_GRP_OPEN and self.current_grp == TOOL_GRP_SHUT:
            self.grp.run_timed(speed_sp=self.grp_speed, stop_action=HOLD, time_sp=5000)

        if state == TOOL_GRP_SHUT and self.current_grp == TOOL_GRP_OPEN:
            self.grp.run_timed(speed_sp=-self.grp_speed, stop_action=HOLD, time_sp=5000)

        self.grp.wait_while(Motor.STATE_RUNNING)
        self.current_grp = state

    def tool_key(self, state):
        if self.current_key == TOOL_KEY_UNKNOWN:
            raise Exception('Unknown key state, please reset before use')

        if state == TOOL_KEY_OPEN and self.current_key == TOOL_KEY_SHUT:
            self.key.run_forever(speed_sp=self.key_speed)
            # Approach key photo cell stop
            while self.zkey.reflected_light_intensity < self.zkey_threshold:
                pass
            run_for_degrees(self.key, self.key_speed, 360, HOLD)

        if state == TOOL_KEY_SHUT and self.current_key == TOOL_KEY_OPEN:
            self.key.run_forever(speed_sp=-self.key_speed)
            # Approach key photo cell stop
            while self.zkey.reflected_light_intensity > self.zkey_threshold:
                pass
            run_for_degrees(self.key, -self.key_speed, 5 * 360, HOLD)

        self.key.wait_while(Motor.STATE_RUNNING)
        self.current_key = state
