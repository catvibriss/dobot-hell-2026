from config import *
from objects.dobots import Dobot, DobotBLE
import asyncio
from objects.accessories import Conveyor
import time

# robots
BASE_ROBOT_DLL = Dobot(BASE_ROBOT_COM, dobot_name="Base", dll_path="./dobot_dll/DobotDllBase.dll")
# HELP_ROBOT = Dobot(HELP_ROBOT_COM, dobot_name="Help", dll_path="./dobot_dll/DobotDllHelp.dll")
# SORT_ROBOT = Dobot(SORT_ROBOT_COM, dobot_name="Sort", dll_path="./dobot_dll/DobotDllSort.dll", has_rail=True)

# BASE_ROBOT = DobotBLE(BASE_DOBOT_BLE_MAC, "Base")
HELP_ROBOT = DobotBLE(HELP_DOBOT_BLE_MAC, "Help")
SORT_ROBOT = DobotBLE(SORT_DOBOT_BLE_MAC, "Sort", has_rail=True)

CONV = Conveyor(BASE_ROBOT_DLL)

# CONV.disable()
CONV.enable(conv_speed=-15000)

async def main():
    return
    # await BASE_ROBOT.connect()
    # await BASE_ROBOT.set_motor(0, 10000.0)
    # # d = await BASE_ROBOT.homing()
    # # print(d)
    # await SORT_ROBOT.connect()
    # await SORT_ROBOT.homing()
    # await asyncio.sleep(3)
    
    # await SORT_ROBOT.move(l=647, z=-100, x=205)
    # await SORT_ROBOT.set_suction_cup(True)
    # await SORT_ROBOT.move(relative=True, z=-7)
    # await SORT_ROBOT.move(relative=True, z=100)
    # await SORT_ROBOT.move(z=70, l=50, x=250)
    # await SORT_ROBOT.set_suction_cup(False)

# asyncio.run(main())