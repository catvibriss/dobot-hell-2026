from dobot_dll import DobotDllType as dType
from objects.dobots import DobotDLL
from objects.exceptions import *
from config import *
import math
import time

class Conveyor:
    def __init__(self, owner: DobotDLL, m_index: int = 0):
        if not isinstance(owner, DobotDLL):
            raise WrongDobotClass("you must use DLL Dobot!")
            return
        
        self.owner = owner 
        self.m_index = m_index

        self._last_freq = 0
        self.disable()

    def _log(self, text: str):
        self.owner._log(f"[CV] {text}")

    def start_work(self):
        self.set_freq(freq=-CONV_WORK_FREQ, smooth=True)

    def disable(self):
        dType.SetEMotor(self.api, self.m_index, 0, 0, 0)

    def set_freq(self, freq: int, smooth: bool = False):
        """
        speed by direct freq
        """
        if abs(freq) > CONV_POSSIBLE_MAX_FREQ:
            sign = lambda x: (x > 0) - (x < 0)
            freq = CONV_POSSIBLE_MAX_FREQ * sign(freq)
            
        if not smooth:
            dType.SetEMotor(self.api, self.m_index, 1, freq, 0)

        self._last_freq = freq

    def set_speed(self, speed: float, smooth: bool = False):
        """
        speed by mm/s
        """
        sPc = 360 / 1.8 * 10 * 16
        mPc = math.pi * 36
        freq = speed * sPc / mPc
        self.set_freq(int(freq), smooth)
