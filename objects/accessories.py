from objects.dobots import DobotDLL
from objects.exceptions import *
from config import *
import time

class Conveyor:
    def __init__(self, owner: DobotDLL, motor_id: int = 0):
        if not isinstance(owner, DobotDLL):
            raise WrongDobotClass("you must use conveyor with DLL Dobot!")
            return
        
        self.owner = owner 
        self._motor_id = motor_id

        self._last_motor_speed = None
        self.disable()

        self._max_speed = CONV_MAX_SPEED
        self._work_speed = -CONV_MOVING_SPEED

    def disable(self):
        self.owner.set_motor(0, motor_id=self._motor_id)
        self._last_motor_speed = 0

    def enable(self, smooth: bool = True, reversed: bool = False, speed: float = None):
        conv_speed = self._work_speed
        if reversed:
            conv_speed = conv_speed * -1
        if speed:
            if abs(speed) <= CONV_MOVING_SPEED:
                conv_speed = speed
            else:
                conv_speed = CONV_POSSIBLE_MAX_SPEED
            
        if smooth:
            step = 100 if conv_speed > self._last_motor_speed else -100
            for i in range(self._last_motor_speed, conv_speed+1, step):
                self.owner.set_motor(speed=i, motor_id=self._motor_id)  
                time.sleep(0.01)      
        else:
            self.owner.set_motor(speed=conv_speed, motor_id=self._motor_id)        

    def set_speed(self, speed: float):
        print(speed)
        self.owner.set_motor(speed=-speed, motor_id=self._motor_id)        