from dobot_api import DobotDllType as dType 
from config import *

def init_robot(port_name, is_rail=False, dll_file=DOBOT_DLL_RELATIVE_PATH):
    print(dll_file)
    print(f"connecting [{port_name}]")
    api = dType.load(dll_file)

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
BASE_ROBOT = init_robot(BASE_ROBOT_COM, dll_file="./dobot_api/DobotDllBase.dll")
HELP_ROBOT = init_robot(HELP_ROBOT_COM, dll_file="./dobot_api/DobotDllHelp.dll")
SORT_ROBOT = init_robot(SORT_ROBOT_COM, dll_file="./dobot_api/DobotDllSort.dll", is_rail=True)

# boxes
BLUE_BOX = [False, False, False, False]
RED_BOX = [False, False, False, False] 
GREEN_BOX = [False, False, False, False] 
YELLOW_BOX = [False, False, False, False] 

def move_robot(api, has_rail=False, relative=False, **kwargs):
    pose = dType.GetPose(api)
    if not pose:
        print("Error: Could not retrieve robot pose.")
        return 0 # Return 0 on failure

    current_x, current_y, current_z, current_r = pose[0], pose[1], pose[2], pose[3]
    current_l = pose[7] if len(pose) > 7 else 0 

    dx = kwargs.get('x', 0 if relative else current_x)
    dy = kwargs.get('y', 0 if relative else current_y)
    dz = kwargs.get('z', 0 if relative else current_z)
    dr = kwargs.get('r', 0 if relative else current_r)
    dl = kwargs.get('l', 0 if relative else current_l)

    if relative:
        target_x, target_y, target_z, target_r = current_x+dx, current_y+dy, current_z+dz, current_r+dr
        target_l = current_l + dl
    else:
        target_x, target_y, target_z, target_r, target_l = dx, dy, dz, dr, dl

    mode = dType.PTPMode.PTPMOVLXYZMode
    
    # Capture the Command Index (queuedCmdIndex) returned by the function
    if has_rail:
        last_index = dType.SetPTPWithLCmd(api, mode, target_x, target_y, target_z, target_r, target_l, isQueued=0)[0]
    else:
        last_index = dType.SetPTPCmd(api, mode, target_x, target_y, target_z, target_r, isQueued=0)[0]

    # Start executing immediately
    # dType.SetQueuedCmdStartExec(api)
    
    # Return the index so we can track it
    # return last_index

import time

def wait_for_robot(api, target_index):
    """
    Blocks execution until the robot has finished the command with the given index.
    """
    if target_index == 0: return # Safety for failed moves
    
    while True:
        # Get the index of the command the robot is currently processing
        current_index = dType.GetQueuedCmdCurrentIndex(api)[0]
        
        # If current matches or exceeds target, the move is done
        if current_index >= target_index:
            break
        
        # Small sleep to prevent maxing out CPU while waiting
        time.sleep(0.1)

# --- ROBOT COMMANDS ---

# --- BASE ROBOT SEQUENCE ---
# for _ in range(10):
#     move_robot(BASE_ROBOT, x=200, y=0, z=50)
#     move_robot(BASE_ROBOT, z=20, relative=False)

#     # --- HELP ROBOT SEQUENCE ---
#     move_robot(HELP_ROBOT, x=200, y=0, z=50)
#     move_robot(HELP_ROBOT, z=20, relative=False)

#     move_robot(SORT_ROBOT, x=200, y=0, z=50)
#     move_robot(SORT_ROBOT, z=20, relative=False, l=100)

# dType.SetHOMECmd(BASE_ROBOT, 0, 0)
# dType.SetHOMECmd(HELP_ROBOT, 0, 0)
# dType.SetHOMECmd(SORT_ROBOT, 0, 0)

move_robot(SORT_ROBOT, has_rail=True, l=RED_BOX_LDPos)
time.sleep(1)
move_robot(SORT_ROBOT, has_rail=True, l=BLUE_BOX_LDPos)
time.sleep(1)
move_robot(SORT_ROBOT, has_rail=True, l=YELLOW_BOX_LDPos)
time.sleep(1)
move_robot(SORT_ROBOT, has_rail=True, l=GREEN_BOX_LDPos)
time.sleep(1)

# TODO: rewrite
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