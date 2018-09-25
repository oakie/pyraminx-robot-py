from flask import Flask
from time import sleep
from ev3dev.auto import Sound

from robot.robot import PyraminxRobot
from const import *

app = Flask(__name__)
robot = PyraminxRobot()


@app.route('/ping')
def ping():
    return 'pong'


@app.route('/execute/<args>')
def execute(args):
    try:
        cmd = args.split(':')
        robot.soft_reset()
        tips = '' if len(cmd) < 2 else cmd[1]
        robot.execute(cmd[0], tips)
        robot.cart.cart_drv(CART_POS_C)
        sleep(1)
        robot.relax()
    except Exception as e:
        return 'error: ' + str(e)
    return 'ok'


@app.route('/flip/<cmd>')
def flip(cmd):
    try:
        robot.soft_reset()
        robot.flip(cmd)
        robot.cart.cart_drv(CART_POS_C)
        sleep(1)
        robot.relax()
    except Exception as e:
        return 'error: ' + str(e)
    return 'ok'


@app.route('/reset')
def reset():
    try:
        robot.reset()
        Sound.speak('Reset complete').wait()
        sleep(1)
        robot.relax()
    except Exception as e:
        return 'error: ' + str(e)
    return 'ok'


if __name__ == '__main__':
    Sound.speak('Pyraminx').wait()
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
