from config import *
from objects.dobots import DobotDLL, DobotBLE
import asyncio
from objects.accessories import *
from objects.sensors import *
import time

# robots
BASE_ROBOT_DLL = DobotDLL(BASE_ROBOT_COM, dobot_name="Base", dll_path="./dobot_dll/DobotDllBase.dll")
# HELP_ROBOT = DobotDLL(HELP_ROBOT_COM, dobot_name="Help", dll_path="./dobot_dll/DobotDllHelp.dll")
# SORT_ROBOT = DobotDLL(SORT_ROBOT_COM, dobot_name="Sort", dll_path="./dobot_dll/DobotDllSort.dll", has_rail=True)

# BASE_ROBOT = DobotBLE(BASE_DOBOT_BLE_MAC, "Base")
HELP_ROBOT = DobotBLE(HELP_DOBOT_BLE_MAC, "Help")
SORT_ROBOT = DobotBLE(SORT_DOBOT_BLE_MAC, "Sort", has_rail=True)

CONV = Conveyor(BASE_ROBOT_DLL)

CONV.enable()

async def main():
    # return
    # await BASE_ROBOT.connect()
    # await BASE_ROBOT.set_motor(0, 10000.0)
    # # d = await BASE_ROBOT.homing()
    # # print(d)
    await SORT_ROBOT.connect()
    # await SORT_ROBOT.homing()
    # await asyncio.sleep(3)
    
    await SORT_ROBOT.move(l=360)
    # await SORT_ROBOT.set_suction_cup(True)
    # await SORT_ROBOT.move(relative=True, z=-7)
    # await SORT_ROBOT.move(relative=True, z=100)
    # await SORT_ROBOT.move(z=70, l=50, x=250)
    # await SORT_ROBOT.set_suction_cup(False)

# asyncio.run(main())