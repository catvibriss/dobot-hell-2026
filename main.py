from config import *
from objects.dobots import DobotDLL, BlankDobotDLL, DobotBLE
from objects.accessories import *
from objects.sensors import *

from gui.app import app
import state

# CONV = Conveyor(BASE_DOBOT, 0)
# COLOR_SENSOR = ColorSensor(BASE_DOBOT)
# OBSTACLE_SENSOR = ObstacleSensor(HELP_DOBOT)

def main():
    state.BASE_DOBOT = DobotDLL(BASE_DOBOT_COM, dobot_name="Base", dll_path="./dobot_dll/DobotDllBase.dll")
    state.CONV = Conveyor(state.BASE_DOBOT, 0)
    # state.HELP_DOBOT = BlankDobotDLL(HELP_DOBOT_COM, "Help")
    # SORT_DOBOT = BlankDobotDLL(SORT_DOBOT_BLE_MAC, "Sort", has_rail=True)
    
    app.mainloop()

if __name__ == "__main__":
    main()