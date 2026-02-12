from config import *
from objects.dobots import DobotDLL, DobotBLE
from objects.accessories import *
from objects.sensors import *

from utils import sorting

# robots
BASE_DOBOT = DobotDLL(BASE_DOBOT_COM, dobot_name="Base", dll_path="./dobot_dll/DobotDllBase.dll")
HELP_DOBOT = DobotBLE(HELP_DOBOT_BLE_MAC, "Help")
SORT_DOBOT = DobotBLE(SORT_DOBOT_BLE_MAC, "Sort", has_rail=True)

CONV = Conveyor(BASE_DOBOT, 0)
COLOR_SENSOR = ColorSensor(BASE_DOBOT)
OBSTACLE_SENSOR = ObstacleSensor(HELP_DOBOT)