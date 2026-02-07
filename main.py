from config import *
from objects.dobots import DobotDLL, DobotBLE
from objects.accessories import *
from objects.sensors import *

from utils import sorting

# robots
BASE_ROBOT = DobotDLL(BASE_ROBOT_COM, dobot_name="Base", dll_path="./dobot_dll/DobotDllBase.dll")
HELP_ROBOT = DobotBLE(HELP_DOBOT_BLE_MAC, "Help")
SORT_ROBOT = DobotBLE(SORT_DOBOT_BLE_MAC, "Sort", has_rail=True)

CONV = Conveyor(BASE_ROBOT)
DIST_SENSOR = DistanceSensor()

# sorting.start_sorting()