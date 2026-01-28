from dobot_dll import DobotDllType as dType
from config import *
import time
from datetime import datetime

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

    def move(self, relative=False, **kwargs):
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
    
    def motor(self, speed: int, motor_id: int):
        dType.SetEMotor(self._api, motor_id, 0 if speed == 0 else 1, int(speed), 0)

    def __del__(self):
        dType.DisconnectDobot(self._api)

class DobotBLE:
    def __init__(self, dobot_mac, dobot_name, has_rail: bool = False):
        self._mac = dobot_mac
        self.name = dobot_name

        self._has_rail = has_rail

        self._connect_ble()

    def _log_print(self, text: str):
        time_now = datetime.now().strftime("%H:%M:%S")
        print(f"[{time_now}] [{self.name}] {text}")

    def _connect_ble(self):
        return

    def _send_command(self):
        return
    
    def _build_command(self):
        return
    
    def current_pose(self):
        return
    
    def move(self):
        return
    
    def homing(self):
        return
    
d = DobotBLE("asdads", "sadasdasd")
d._log_print("fdsf")