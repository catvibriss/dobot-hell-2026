from dobot_dll import DobotDllType as dType
from objects.dobots import DobotDLL
from objects.exceptions import *

class ColorSensor:
    def __init__(self, owner: DobotDLL):
        if not isinstance(owner, DobotDLL):
            raise WrongDobotClass("you must use conveyor with DLL Dobot!")
            return

        self.owner = owner

class DistanceSensor:
    def __init__(self, owner: DobotDLL):
        if not isinstance(owner, DobotDLL):
            raise WrongDobotClass("you must use conveyor with DLL Dobot!")
            return

        self.owner = owner