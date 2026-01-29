from dobot_dll import DobotDllType as dType
from config import *
from datetime import datetime
from bleak import BleakClient
import asyncio
import struct

class DobotDLL:
    def __init__(self, com_port: str, dll_path: str, dobot_name: str = "Dobot", has_rail: bool = False):
        self.api = None
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

        self.api = api

    def _stop_and_clear_queue(self):
        dType.SetQueuedCmdStopExec(self.api)
        dType.SetQueuedCmdClear(self.api)

    def _start_queue(self):
        dType.SetQueuedCmdStartExec(self.api)

    def move(self, relative=False, **kwargs):
        pose = dType.GetPose(self.api)
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

        self._stop_and_clear_queue()
        mode = dType.PTPMode.PTPMOVLXYZMode

        if self._has_rail:
            last_index = dType.SetPTPWithLCmd(self.api, mode, target_x, target_y, target_z, target_r, target_l, isQueued=1)[0]
        else:
            last_index = dType.SetPTPCmd(self.api, mode, target_x, target_y, target_z, target_r, isQueued=1)[0]

        self._start_queue()

        while True:
            current_cmd_index = dType.GetQueuedCmdCurrentIndex(self.api)[0]
            if current_cmd_index >= last_index:
                break
            dType.dSleep(100) 

        self._stop_and_clear_queue()
    
    def set_motor(self, speed: int, motor_id: int):
        dType.SetEMotor(self.api, motor_id, 0 if speed == 0 else 1, int(speed), 0)

    def homing(self):
        dType.SetHOMECmdEx(self.api)

    def current_pose(self):
        response = dType.GetPose(self.api)
        if self._has_rail:
            response["l"] = dType.GetPoseL(self.api)

        return response

class DobotBLE:
    SERVICE_UUID = "0003CDD0-0000-1000-8000-00805F9B0131"
    WRITE_UUID   = "0003CDD2-0000-1000-8000-00805F9B0131"
    READ_UUID    = "0003CDD1-0000-1000-8000-00805F9B0131"

    def __init__(self, dobot_mac, dobot_name, has_rail: bool = False):
        self._mac = dobot_mac
        self.name = dobot_name
        self._has_rail = has_rail

        self.client = None
        self._pending_future = None
        self._expected_cmd_id = None

    def _log(self, text: str):
        time_now = datetime.now().strftime("%H:%M:%S")
        print(f"[{time_now}] [{self.name}] {text}")

    async def connect(self):
        self._log(f"Connecting to {self._mac}...")
        try:
            self.client = BleakClient(self._mac)
            await self.client.connect()
            await self.client.start_notify(self.READ_UUID, self._notification_handler)
            
            await self._dobot_setup()
            
            self._log("Connected and Setup Complete.")
            return True
        except Exception as e:
            self._log(f"Connection failed: {e}")
            return False

    async def disconnect(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            self._log("Disconnected.")

    async def _dobot_setup(self):
        self._log("Running Setup...")
        
        await self._send_command(cmd_id=245, rw=1, is_queued=0)

        params_joint = struct.pack('<8f', 200.0, 200.0, 200.0, 200.0, 200.0, 200.0, 200.0, 200.0)
        await self._send_command(cmd_id=80, params=params_joint, rw=1, is_queued=0)

        params_coord = struct.pack('<4f', 200.0, 200.0, 200.0, 200.0)
        await self._send_command(cmd_id=81, params=params_coord, rw=1, is_queued=0)

        params_common = struct.pack('<2f', 100.0, 100.0)
        await self._send_command(cmd_id=83, params=params_common, rw=1, is_queued=0)

        if self._has_rail:
            params_rail_l = struct.pack('<2f', 200.0, 100.0)
            await self._send_command(cmd_id=85, params=params_rail_l, rw=1, is_queued=0)

            params_enable_rail = struct.pack('<BB', 1, 1)
            await self._send_command(cmd_id=3, params=params_enable_rail, rw=1, is_queued=0)

    async def _stop_and_clear_queue(self):
        await self._send_command(cmd_id=241, rw=1, is_queued=0)
        await self._send_command(cmd_id=245, rw=1, is_queued=0)

    async def _start_queue(self):
        await self._send_command(cmd_id=240, rw=1, is_queued=0)

    async def _wait_for_command(self, target_index):
        self._log(f"Waiting for command index {target_index}...")
        while True:
            resp = await self._send_command(cmd_id=246, rw=0, is_queued=0)
            if resp:
                curr_idx = struct.unpack('<Q', resp[:8])[0]
                if curr_idx >= target_index:
                    break
            await asyncio.sleep(0.1)
        self._log("Command execution finished.")

    async def set_motor(self, index: int, speed: float, is_enabled: bool = True):
        self._log(f"Setting Motor {index}: Speed={speed}, Enabled={is_enabled}")
        
        await self._stop_and_clear_queue()
        
        params = struct.pack('<BBf', index, int(is_enabled), speed)
        resp = await self._send_command(cmd_id=135, params=params, rw=1, is_queued=0)
        
        last_index = 0
        if resp:
            last_index = struct.unpack('<Q', resp[:8])[0]

        await self._start_queue()  
        await self._wait_for_command(last_index)
        await self._stop_and_clear_queue()

    async def get_motor(self):
        resp = await self._send_command(cmd_id=135, rw=0, is_queued=0)
        if resp and len(resp) >= 6:
            idx, enabled, speed = struct.unpack('<BBf', resp[:6])
            self._log(f"Motor Status: Index={idx}, Enabled={enabled}, Speed={speed}")
            return {"index": idx, "enabled": bool(enabled), "speed": speed}
        return None

    async def set_suction_cup(self, active: bool):
        self._log(f"Setting Suction Cup: {'ON' if active else 'OFF'}")
        await self._stop_and_clear_queue()
        
        last_index = 0
        enable_ctrl = 1
        is_sucked = 1 if active else 0

        params = struct.pack('<BB', enable_ctrl, is_sucked)
        resp = await self._send_command(cmd_id=62, params=params, rw=1, is_queued=1)

        if resp:
            last_index = struct.unpack('<Q', resp[:8])[0]

        await self._start_queue()
        await self._wait_for_command(last_index)
        await self._stop_and_clear_queue()

    async def set_gripper(self, status: str):
        status = status.lower()
        self._log(f"Setting Gripper: {status}")
        await self._stop_and_clear_queue()
        
        last_index = 0
        enable_ctrl = 0
        is_gripped = 0

        if status in ["grip", "close"]:
            enable_ctrl = 1
            is_gripped = 1
        elif status in ["release", "open"]:
            enable_ctrl = 1
            is_gripped = 0
        elif status == "off":
            enable_ctrl = 0
            is_gripped = 0

        params = struct.pack('<BB', enable_ctrl, is_gripped)
        resp = await self._send_command(cmd_id=63, params=params, rw=1, is_queued=1)

        if resp:
            last_index = struct.unpack('<Q', resp[:8])[0]

        await self._start_queue()
        await self._wait_for_command(last_index)
        await self._stop_and_clear_queue()

    async def current_pose(self):
        resp_arm = await self._send_command(cmd_id=10, rw=0, is_queued=0)
        if not resp_arm:
            self._log("Failed to get Arm Pose.")
            return None
        
        arm_data = struct.unpack('<8f', resp_arm[:32])
        pose = {
            "x": arm_data[0], "y": arm_data[1], "z": arm_data[2], "r": arm_data[3],
            "joints": arm_data[4:],
            "l": 0.0
        }

        if self._has_rail:
            resp_rail = await self._send_command(cmd_id=13, rw=0, is_queued=0)
            if resp_rail:
                pose["l"] = struct.unpack('<f', resp_rail[:4])[0]
        
        return pose

    async def homing(self):
        self._log("Starting Homing...")
        await self._stop_and_clear_queue()
        
        params = struct.pack('<I', 0)
        resp = await self._send_command(cmd_id=31, params=params, rw=1, is_queued=1)
        
        last_index = struct.unpack('<Q', resp[:8])[0] if resp else 0

        await self._start_queue()
        await self._wait_for_command(last_index)
        await self._stop_and_clear_queue()
        self._log("Homing Complete.")

    async def move(self, relative=False, **kwargs):
        await self._stop_and_clear_queue()
        
        curr = await self.current_pose()
        if not curr:
            return

        tx = kwargs.get('x', 0 if relative else curr['x'])
        ty = kwargs.get('y', 0 if relative else curr['y'])
        tz = kwargs.get('z', 0 if relative else curr['z'])
        tr = kwargs.get('r', 0 if relative else curr['r'])
        tl = kwargs.get('l', 0 if relative else curr['l'])

        if relative:
            tx += curr['x']; ty += curr['y']; tz += curr['z']; tr += curr['r']; tl += curr['l']

        self._log(f"Moving to: X={tx:.2f}, Y={ty:.2f}, Z={tz:.2f}, R={tr:.2f}, L={tl:.2f}")

        ptp_mode = 2
        last_index = 0

        if self._has_rail:
            params = struct.pack('<B5f', ptp_mode, tx, ty, tz, tr, tl)
            resp = await self._send_command(cmd_id=86, params=params, rw=1, is_queued=1)
        else:
            params = struct.pack('<B4f', ptp_mode, tx, ty, tz, tr)
            resp = await self._send_command(cmd_id=84, params=params, rw=1, is_queued=1)

        if resp:
            last_index = struct.unpack('<Q', resp[:8])[0]

        await self._start_queue()
        await self._wait_for_command(last_index)
        await self._stop_and_clear_queue()

    def _notification_handler(self, sender, data: bytearray):
        if len(data) < 5 or data[0] != 0xAA or data[1] != 0xAA:
            return

        payload_len = data[2]
        cmd_id = data[3]
        payload = data[3 : 3 + payload_len]
        
        if self._calculate_checksum(payload) != data[3 + payload_len]:
            self._log(f"Checksum Error on ID {cmd_id}")
            return

        params = data[5 : 3 + payload_len]

        if self._pending_future and not self._pending_future.done():
            if self._expected_cmd_id == cmd_id:
                self._pending_future.set_result(params)

    def _calculate_checksum(self, payload):
        return (256 - sum(payload) % 256) % 256

    async def _send_command(self, cmd_id, params=b"", rw=1, is_queued=0, timeout=3.0):
        if not self.client or not self.client.is_connected:
            self._log("Not connected.")
            return None

        ctrl = rw | (is_queued << 1)
        payload = bytes([cmd_id, ctrl]) + params
        packet = bytes([0xAA, 0xAA, len(payload)]) + payload + bytes([self._calculate_checksum(payload)])

        self._expected_cmd_id = cmd_id
        self._pending_future = asyncio.Future()

        try:
            await self.client.write_gatt_char(self.WRITE_UUID, packet)
            return await asyncio.wait_for(self._pending_future, timeout)
        except asyncio.TimeoutError:
            self._log(f"Timeout waiting for response to ID {cmd_id}")
            return None
        finally:
            self._pending_future = None
            self._expected_cmd_id = None