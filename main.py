from dobot_api import DobotDllType as dType 
from config import *
import time

class Dobot:
    def __init__(self, com_port: str, dll_path: str, dobot_name: str = "Dobot", has_rail: bool = False):
        self._api = None
        self.name = dobot_name

        self._com_port = com_port
        self._dll_path = dll_path
        self._has_rail = has_rail

        self._init_dType()

    def _init_dType(self):
        api = dType.load(self._dll_path)

        state = dType.ConnectDobot(api, self._com_port, 115200)
        if state[0] != dType.DobotConnect.DobotConnect_NoError:
            print(f"[{self.name}] failed")
            return None

        print(f"[{self.name}] connected")
        
        dType.SetQueuedCmdClear(api)
        dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200)
        dType.SetPTPCoordinateParams(api, 200, 200, 200, 200)
        dType.SetPTPCommonParams(api, 100, 100)
        
        if self._has_rail:
            dType.SetPTPLParams(api, 200, 100)
            dType.SetDeviceWithL(api, 1, 1)

        self._api = api

    def move_robot(self, relative=False, **kwargs):
        pose = dType.GetPose(self._api)
        if not pose:
            print("Error: Could not retrieve robot pose.")
            return 0

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

        dType.SetQueuedCmdStopExec(self._api)
        dType.SetQueuedCmdClear(self._api)

        mode = dType.PTPMode.PTPMOVLXYZMode

        if self._has_rail:
            last_index = dType.SetPTPWithLCmd(self._api, mode, target_x, target_y, target_z, target_r, target_l, isQueued=1)[0]
        else:
            last_index = dType.SetPTPCmd(self._api, mode, target_x, target_y, target_z, target_r, isQueued=1)[0]

        dType.SetQueuedCmdStartExec(self._api)

        while True:
            current_cmd_index = dType.GetQueuedCmdCurrentIndex(self._api)[0]
            if current_cmd_index >= last_index:
                break
            dType.dSleep(100) 

        dType.SetQueuedCmdStopExec(self._api)
        dType.SetQueuedCmdClear(self._api)

        return last_index
    
    def control_motor(self, speed: int, motor_id: int):
        dType.SetEMotor(self._api, motor_id, 0 if speed == 0 else 1, int(speed), 0)

    def __del__(self):
        dType.DisconnectDobot(self._api)

class Conveyor:
    def __init__(self, owner: Dobot, motor_id: int = 0):
        self.owner = owner 
        self._motor_id = motor_id

        self._last_motor_speed = None
        self.disable()

        self._max_speed = CONV_MAX_SPEED
        self._work_speed = -CONV_MOVING_SPEED

    def disable(self):
        self.owner.control_motor(0, motor_id=self._motor_id)
        self._last_motor_speed = 0

    def enable(self, smooth: bool = True, reversed: bool = False):
        speed = self._work_speed
        if reversed:
            speed = speed * -1

        if smooth:
            step = 100 if speed > self._last_motor_speed else -100
            for i in range(self._last_motor_speed, speed+1, step):
                self.owner.control_motor(speed=i, motor_id=self._motor_id)  
                time.sleep(0.01)      
        else:
            self.owner.control_motor(speed=speed, motor_id=self._motor_id)        

# robots
BASE_ROBOT = Dobot(BASE_ROBOT_COM, dobot_name="Base", dll_path="./dobot_api/DobotDllBase.dll")
HELP_ROBOT = Dobot(HELP_ROBOT_COM, dobot_name="Help", dll_path="./dobot_api/DobotDllHelp.dll")
SORT_ROBOT = Dobot(SORT_ROBOT_COM, dobot_name="Sort", dll_path="./dobot_api/DobotDllSort.dll", has_rail=True)

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