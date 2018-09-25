

def run_for_degrees(motor, speed, degrees, stop=None):
    motor.position = 0
    motor.run_forever(speed_sp=speed)
    while abs(motor.position) < degrees:
        pass
    if stop is not None:
        motor.stop(stop_action=stop)


def run_until_stalled(motor, speed, stop=None):
    motor.run_forever(speed_sp=speed)
    motor.wait_until('stalled')
    if stop is not None:
        motor.stop(stop_action=stop)
