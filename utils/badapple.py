from objects.dobots import DobotDLL
from dobot_dll import DobotDllType as dType

class EMotor:
    def __init__(self, owner: DobotDLL, motor_id: int = 0):
        self.owner = owner
        self.motor_id = motor_id

        self.min_freq = 0
        self.max_freq = 0
        self.min_freq_speed = 0
        self.max_freq_speed = 0

    def set_speed(self, speed: float):
        dType.SetEMotor(self.owner, self.motor_id, 1 if speed!= 0 else 0, speed, 0)

    def play_freq(self, freq: float):
        if freq not in range(self.min_freq, self.max_freq):
            raise ValueError
        
        mapped = (freq - self.min_freq) * (self.max_freq_speed - self.min_freq_speed) / (self.max_freq - self.min_freq) + self.min_freq_speed
        self.set_speed(mapped)

# IDEA: испольщуется два мотора
# один для баса, второй для вокала/высоких частот
# итог: total bad apple
# DLL доботы потому что по проводу = профит: нет задержек