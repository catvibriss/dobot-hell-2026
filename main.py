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
BASE_ROBOT = init_robot(BASE_ROBOT_COM)
HELP_ROBOT = init_robot("COM5")

# boxes
BLUE_BOX = [False, False, False, False]
RED_BOX = [False, False, False, False] 
GREEN_BOX = [False, False, False, False] 
YELLOW_BOX = [False, False, False, False] 

def move_robot(api, has_rail=False, relative=False, **kwargs):
    """
    Moves the robot to a target position.
    
    Args:
        api: The connected robot object.
        has_rail (bool): Whether to use the rail command (L-axis).
        relative (bool): If True, coordinates are added to the current position.
        **kwargs: Target coordinates (x, y, z, r, l).
    """
    pose = dType.GetPose(api)
    
    if not pose:
        print("Error: Could not retrieve robot pose.")
        return

    current_x, current_y, current_z, current_r = pose[0], pose[1], pose[2], pose[3]
    current_l = pose[7] if len(pose) > 7 else 0 

    # target
    dx = kwargs.get('x', 0 if relative else current_x)
    dy = kwargs.get('y', 0 if relative else current_y)
    dz = kwargs.get('z', 0 if relative else current_z)
    dr = kwargs.get('r', 0 if relative else current_r)
    dl = kwargs.get('l', 0 if relative else current_l)

    if relative:
        target_x = current_x + dx
        target_y = current_y + dy
        target_z = current_z + dz
        target_r = current_r + dr
        target_l = current_l + dl
    else:
        target_x, target_y, target_z, target_r, target_l = dx, dy, dz, dr, dl

    # execute 
    mode = dType.PTPMode.PTPMOVLXYZMode

    if has_rail:
        dType.SetPTPWithLCmd(api, mode, target_x, target_y, target_z, target_r, target_l, isQueued=1)
    else:
        dType.SetPTPCmd(api, mode, target_x, target_y, target_z, target_r, isQueued=1)

# Move to approach position
move_robot(BASE_ROBOT, x=200, y=0, z=100)

# Move down to pick
move_robot(BASE_ROBOT, z=-20, relative=True)

# Move back up
move_robot(BASE_ROBOT, z=20, relative=True)

# Execute all queued commands
dType.SetQueuedCmdStartExec(BASE_ROBOT)

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