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
base_note = 10000
half_tone = 1320
eighth = 0.2

do0_di = 4450
re0 = 4700
re0_di = 5000
mi0 = 5280
fa0 = 5570
fa0_di = 5920
salt0 = 6330
salt0_di = 6650
la0 = 7050
la0_di = 7470
si0 = 7900
do = 8400
do_di = 8870
re = 9400
re_di = 9950
mi = 10500
fa = 11170
fa_di = 11800
salt = 12520
salt_di = 13250
la = 14100
la_di = 14900
si = 15800
do2 = 16800
do_di2 = 17700
re2 = 18700
re_di2 = 19900

CONV = Conveyor(BASE_ROBOT_DLL)

CONV.enable(speed=7500)
time.sleep(5)
CONV.disable()
exit()

# CONV.disable()
# CONV.enable(speed=-10000)

#bad_apple

#sq 1
CONV.set_speed(base_note)
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*12))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note)
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)

CONV.set_speed(base_note)
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note)
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note)
time.sleep(eighth)
CONV.set_speed(base_note-half_tone)
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)

CONV.set_speed(0)

#sq 2
CONV.set_speed(base_note)
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*12))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note)
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)

CONV.set_speed(base_note)
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)

#sq 3
CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*12))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*12))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)


CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note-(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note)
time.sleep(eighth*2)
CONV.set_speed(base_note-(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note)
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note)
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)

#sq 4
CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*12))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*12))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*12))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*14))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*17))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*15))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*14))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note-(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note)
time.sleep(eighth*2)

CONV.set_speed(0)

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