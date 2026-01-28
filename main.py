from dobot_api import DobotDllType as dType 
from config import *
import time

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
# dType.ClearAllAlarmsState(BASE_ROBOT)
# boxes
BLUE_BOX = [False, False, False, False]
RED_BOX = [False, False, False, False] 
GREEN_BOX = [False, False, False, False] 
YELLOW_BOX = [False, False, False, False] 

def move_robot(api, has_rail=False, relative=False, **kwargs):
    # --- 1. GET CURRENT POSITION ---
    pose = dType.GetPose(api)
    if not pose:
        print("Error: Could not retrieve robot pose.")
        return 0

    current_x, current_y, current_z, current_r = pose[0], pose[1], pose[2], pose[3]
    current_l = pose[7] if len(pose) > 7 else 0 

    # --- 2. CALCULATE TARGETS ---
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

    # --- 3. PRE-MOVE CLEANUP (The "Fresh Start" Logic) ---
    # Stop any previous execution and wipe the queue so index starts at 0
    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)

    # --- 4. SEND COMMAND ---
    mode = dType.PTPMode.PTPMOVLXYZMode
    
    # We use isQueued=1 (Buffered) because it is more stable than Immediate mode,
    # even though we are executing it right away.
    if has_rail:
        last_index = dType.SetPTPWithLCmd(api, mode, target_x, target_y, target_z, target_r, target_l, isQueued=1)[0]
    else:
        last_index = dType.SetPTPCmd(api, mode, target_x, target_y, target_z, target_r, isQueued=1)[0]

    # --- 5. EXECUTE AND WAIT ---
    dType.SetQueuedCmdStartExec(api)

    # Block Python until the robot catches up to the command index
    while True:
        current_cmd_index = dType.GetQueuedCmdCurrentIndex(api)[0]
        if current_cmd_index >= last_index:
            break
        dType.dSleep(100) # Small pause to save CPU

    # --- 6. POST-MOVE CLEANUP ---
    # Stop execution immediately so the robot is "Safe" and "Idle"
    dType.SetQueuedCmdStopExec(api)
    dType.SetQueuedCmdClear(api)

    return last_index

def toggle_conveyor(api, enable=True, speed=5000):
    """
    Controls the conveyor belt connected to Stepper 1 (E1) immediately.
    """
    # 0 = Stepper 1
    # 1/0 = Enable/Disable
    # speed = Speed (steps/sec)
    # isQueued = 0 (Execute Immediately)
    dType.SetEMotor(api, 0, 1 if enable else 0, int(speed), 0)

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

# toggle_conveyor(BASE_ROBOT, speed=0)
# time.sleep(3)
# move_robot(BASE_ROBOT, x=CONV_BASE_3DPOS[0], y=CONV_BASE_3DPOS[1], z=CONV_BASE_3DPOS[2]+10)
print(dType.GetAlarmsState(BASE_ROBOT))
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