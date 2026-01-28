from config import *
from objects.dobots import Dobot
from objects.accessories import Conveyor

# robots
BASE_ROBOT = Dobot(BASE_ROBOT_COM, dobot_name="Base", dll_path="./dobot_dll/DobotDllBase.dll")
HELP_ROBOT = Dobot(HELP_ROBOT_COM, dobot_name="Help", dll_path="./dobot_dll/DobotDllHelp.dll")
SORT_ROBOT = Dobot(SORT_ROBOT_COM, dobot_name="Sort", dll_path="./dobot_dll/DobotDllSort.dll", has_rail=True)

CONV = Conveyor(BASE_ROBOT)

# boxes
BLUE_BOX = [False, False, False, False]
RED_BOX = [False, False, False, False] 
GREEN_BOX = [False, False, False, False] 
YELLOW_BOX = [False, False, False, False] 

def cube_sort_pos(color: int):
    box = []
    box_ldpos = [0, BOX_CONST_X]
    move_pos = []

    match color:
        case 0: # blue
            box = BLUE_BOX
            box_ldpos[0] = BLUE_BOX_LDPos
        case 1: # red
            box = RED_BOX
            box_ldpos[0] = RED_BOX_LDPos
        case 2: # green
            box = GREEN_BOX
            box_ldpos[0] = GREEN_BOX_LDPos
        case 3: # yellow
            box = YELLOW_BOX
            box_ldpos[0] = YELLOW_BOX_LDPos
    
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