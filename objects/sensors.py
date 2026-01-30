from dobot_dll import DobotDllType as dType
from objects.dobots import DobotDLL
from objects.exceptions import *
import threading
import time

class ColorSensor:
    def __init__(self, owner: DobotDLL):
        if not isinstance(owner, DobotDLL):
            raise WrongDobotClass("you must use conveyor with DLL Dobot!")
            return

        self.owner = owner

    def get_color(self):
        rgb_color = dType.GetColorSensor(self.owner)
        return rgb_color

    def classify_color(self):
        rgb = self.get_color()
        
        is_r = rgb[0] in range(200, 255)
        is_g = rgb[1] in range(200, 255)
        is_b = rgb[2] in range(200, 255)

        if not is_r and not is_g and not is_b:
            return -1
        if is_r and not is_g and not is_b:
            return 3
        if is_r and is_g and not is_b:
            return 2
        if not is_r and is_g and not is_b:
            return 1
        if not is_r and not is_g and is_b:
            return 0
            
class DistanceSensor:
    def __init__(self, owner: DobotDLL, port: int = 0, check_loop_pause: float = 0.05, cancel_loop: bool = False):
        if not isinstance(owner, DobotDLL):
            raise WrongDobotClass("you must use conveyor with DLL Dobot!")
            return
        
        self.owner = owner
        self.port = port
        
        self._check_loop_pause = check_loop_pause
        self._last_value = 0
        
        self._on_change_handlers = []
        self._check_thread = None
        self._check_thread_flag = None

        if not cancel_loop:
            self.start_check()

    def get_distance(self):
        value = dType.GetInfraredSensor(self.owner, self.port)
        return value
    
    def on_change(self, func):
        '''
        Usage example:
        ```
        sensor = DistanceSensor(**params)

        @sensor.on_change
        def hadler(value):
        # do something
        ```
        '''
        self._on_change_handlers.append(func)

    def start_check(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
    
    def stop_check(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
    
    def _loop(self):
        while self._running:
            current = self.get_distance()
            if current != self._last_value:
                self._last_value = current
                self._trigger(current)
            time.sleep(self._check_loop_pause)
    
    def _trigger(self, value):
        for handler in self._on_change_handlers:  
            handler(value)
    