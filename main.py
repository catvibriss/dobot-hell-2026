from config import *
from objects.dobots import DobotDLL, BlankDobotDLL, DobotBLE
from objects.accessories import *
from objects.sensors import *

import state

import asyncio

# CONV = Conveyor(BASE_DOBOT, 0)
# COLOR_SENSOR = ColorSensor(BASE_DOBOT)
# OBSTACLE_SENSOR = ObstacleSensor(HELP_DOBOT)

async def sort_connect():
    state.SORT_DOBOT = DobotBLE(SORT_DOBOT_BLE_MAC, "Sort", has_rail=True)
    await state.SORT_DOBOT.connect()

def main():
    asyncio.run(sort_connect())
    state.BASE_DOBOT = DobotDLL(BASE_DOBOT_COM, dobot_name="Base", dll_path="./dobot_dll/DobotDllBase.dll")
    state.CONV = Conveyor(state.BASE_DOBOT, 0)
    state.HELP_DOBOT = DobotDLL(HELP_DOBOT_COM, dobot_name="Help", dll_path="./dobot_dll/DobotDllHelp.dll")
    state.OBSTACLE = ObstacleSensor(state.HELP_DOBOT, 2, 1)
    state.OBSTACLE._start_loop()

    from gui.app import app
    app.mainloop()

if __name__ == "__main__":
    main()