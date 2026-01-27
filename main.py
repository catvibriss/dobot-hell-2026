from dobot_api import DobotDllType as dType 
from config import *

def init_robot(port_name, is_rail=False):
    print(f"connecting [{port_name}]")
    api = dType.load()

    state = dType.ConnectDobot(api, port_name, 115200)
    if state[0] != dType.DobotConnect.DobotConnect_NoError:
        print(f"[{port_name}] failed")
        return None

    print(f"[{port_name}] connected")
    
    dType.SetQueuedCmdClear(api)
    dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200)
    dType.SetPTPCoordinateParams(api, 200, 200, 200, 200)
    dType.SetPTPCommonParams(api, 100, 100)
    
    if is_rail:
        dType.SetPTPLParams(api, 200, 100)
        dType.SetDeviceWithL(api, 1, 1)

    return api

# robots
RAIL_ROBOT = init_robot("COM8", is_rail=True)
BASE_ROBOT = init_robot("COM4")
HELP_ROBOT = init_robot("COM5")

# boxes
BLUE_BOX = [False, False, False, False]
RED_BOX = [False, False, False, False] 
GREEN_BOX = [False, False, False, False] 
YELLOW_BOX = [False, False, False, False] 

def cube_sort_pos(color: int):
    box = []
    box_ldpos = []
    move_pos = []

    match color:
        case 0: # blue
            box = BLUE_BOX
            box_ldpos = BLUE_BOX_LDPos
        case 1: # red
            box = RED_BOX
            box_ldpos = RED_BOX_LDPos
        case 2: # green
            box = GREEN_BOX
            box_ldpos = GREEN_BOX_LDPos
        case 3: # yellow
            box = YELLOW_BOX
            box_ldpos = YELLOW_BOX_LDPos
    
    free_space_idx = box.index(False)
    match free_space_idx:
        case 0:
            move_pos = box_ldpos
        case 1:
            box_ldpos[0] += BOX_X_OFFSET
            move_pos = box_ldpos
        case 2:
            box_ldpos[1] -= BOX_Y_OFFSET
            move_pos = box_ldpos
        case 3:
            box_ldpos[0] += BOX_X_OFFSET
            box_ldpos[1] -= BOX_Y_OFFSET
            move_pos = box_ldpos
    
    box[free_space_idx] = True
    return move_pos