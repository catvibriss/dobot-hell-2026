from dobot_dll import DobotDllType as dType
from objects.dobots import DobotDLL
from objects.exceptions import *
import threading
import time

class ColorSensor:
    def __init__(self, owner: DobotDLL, port: int = 1, version: int = 0):
        if not isinstance(owner, DobotDLL):
            raise WrongDobotClass("you must use DLL Dobot!")

        self.owner = owner
        self.port = port
        self.version = version

        self._enabled = False

    def _log(self, text: str):
        self.owner._log(f"[CS] {text}")

    def enable(self):
        self._log("enabled")
        dType.SetColorSensor(self.owner.api, 1, self.port, self.version)
        self._enabled = True

    def disable(self):
        self._log("disabled")
        dType.SetColorSensor(self.owner.api, 0, self.port, self.version)
        self._enabled = False

    def current_color(self, force: bool = False):
        rgb = None
        if not self._enabled:
            if force:
                self._log("forced measure")
                self.enable()
                rgb = dType.GetColorSensor(self.owner.api)
                self.disable()
        else:
            rgb = dType.GetColorSensor(self.owner.api)
        return rgb

class ObstacleSensor:
    def __init__(self, owner: DobotDLL, port: int = 1, version: int = 0):
        if not isinstance(owner, DobotDLL):
            raise WrongDobotClass("you must use DLL Dobot!")

        self.owner = owner
        self.port = port
        self.version = version

        self._enabled = False

        self._loop_handlers = []
        self._last_state = 0
        self._thread = None
        self._thread_is_running = False

        self._start_loop()

    def _log(self, text: str):
        self.owner._log(f"[OS] {text}")

    def on_obstacle(self, func):
        self._loop_handlers.append(func)

    def _loop_trigger(self):
        self._log("obstacle loop triggered")
        for func in self._loop_handlers[:]:
            func()

    def _loop(self):
        while self._thread_is_running:
            current = self.state()
            if current != self._last_state:
                if current == 1 and self._last_state == 0:
                    self._loop_trigger()
                self._last_state = current
            time.sleep(0.01)

    def _start_loop(self):
        if self._thread_is_running:
            return

        self._thread_is_running = True
        self._thread = threading.Thread(target=self._loop)
        self._thread.start()
        
    def _stop_loop(self):
        if not self._thread_is_running:
            return
        
        self._thread_is_running = False
        if self._thread is not None:
            self._thread.join()

    def enable(self):
        self._log("enabled")
        dType.SetInfraredSensor(self.owner.api, 1, self.port, self.version)
        self._enabled = True

    def disable(self):
        self._log("disabled")
        dType.SetInfraredSensor(self.owner.api, 0, self.port, self.version)
        self._enabled = False

    def state(self, force: bool = False):
        current_state = None
        if not self._enabled:
            if force:
                self._log("forced state")
                self.enable()
                current_state = dType.GetInfraredSensor(self.owner.api, self.port)[0]        
                self.disable()
        else:
            current_state = dType.GetInfraredSensor(self.owner.api, self.port)[0]        
        return current_state