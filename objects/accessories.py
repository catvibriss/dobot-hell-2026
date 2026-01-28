from objects.dobots import Dobot
from config import *
import time

class Conveyor:
    def __init__(self, owner: Dobot, motor_id: int = 0):
        self.owner = owner 
        self._motor_id = motor_id

        self._last_motor_speed = None
        self.disable()

        self._max_speed = CONV_MAX_SPEED
        self._work_speed = -CONV_MOVING_SPEED

    def disable(self):
        self.owner.control_motor(0, motor_id=self._motor_id)
        self._last_motor_speed = 0

    def enable(self, smooth: bool = True, reversed: bool = False):
        speed = self._work_speed
        if reversed:
            speed = speed * -1

        if smooth:
            step = 100 if speed > self._last_motor_speed else -100
            for i in range(self._last_motor_speed, speed+1, step):
                self.owner.control_motor(speed=i, motor_id=self._motor_id)  
                time.sleep(0.01)      
        else:
            self.owner.control_motor(speed=speed, motor_id=self._motor_id)        
