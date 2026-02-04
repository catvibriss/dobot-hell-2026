from objects.dobots import DobotDLL
from dobot_dll import DobotDllType as dType
from main import *

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
exit()
base_note = 10000
half_tone = 1320
eighth = 0.2

do0_di = 4450
re0 = 4700
re0_di = 5000
mi0 = 5280
fa0 = 5570
fa0_di = 5920
salt0 = 6330
salt0_di = 6650
la0 = 7050
la0_di = 7470
si0 = 7900
do = 8400
do_di = 8870
re = 9400
re_di = 9950
mi = 10500
fa = 11170
fa_di = 11800
salt = 12520
salt_di = 13250
la = 14100
la_di = 14900
si = 15800
do2 = 16800
do_di2 = 17700
re2 = 18700
re_di2 = 19900

CONV = Conveyor(BASE_ROBOT_DLL)

# s = 35000
# for i in range(0, s, s//10):
#     CONV.set_speed(speed=i)
#     time.sleep(0.3)
# CONV.set_speed(speed=s)
# time.sleep(5)
# CONV.disable()
# exit()

# CONV.disable()
# CONV.enable(speed=-10000)

#bad_apple

#sq 1
CONV.set_speed(base_note)
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*12))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note)
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)

CONV.set_speed(base_note)
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note)
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note)
time.sleep(eighth)
CONV.set_speed(base_note-half_tone)
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)

CONV.set_speed(0)

#sq 2
CONV.set_speed(base_note)
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*12))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note)
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)

CONV.set_speed(base_note)
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)

#sq 3
CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*12))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*12))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)


CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note-(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note)
time.sleep(eighth*2)
CONV.set_speed(base_note-(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note)
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note)
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)

#sq 4
CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*12))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*12))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*12))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*14))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*17))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*15))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*14))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*10))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth*2)
CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*7))
time.sleep(eighth)

CONV.set_speed(base_note+(half_tone*5))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*3))
time.sleep(eighth)
CONV.set_speed(base_note+(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note-(half_tone*2))
time.sleep(eighth)
CONV.set_speed(base_note)
time.sleep(eighth*2)

CONV.set_speed(0)

# == == == == ==

# s = 35000
# for i in range(0, s, s//10):
#     CONV.set_speed(speed=i)
#     time.sleep(0.3)
# CONV.set_speed(speed=s)
# time.sleep(5)
# CONV.disable()
# exit()

do0_di = 4450
re0 = 4700
re0_di = 5000
mi0 = 5280
fa0 = 5570
fa0_di = 5920
salt0 = 6330
salt0_di = 6650
la0 = 7050
la0_di = 7470
si0 = 7900
do = 8400
do_di = 8870
re = 9400
re_di = 9950
mi = 10500
fa = 11170
fa_di = 11800
salt = 12520
salt_di = 13250
la = 14100
la_di = 14900
si = 15800
do2 = 16800
do2_di = 17700
re2 = 18700
re2_di = 19900

CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=re_di)
time.sleep(0.25)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=do_di)
time.sleep(0.75)
CONV.enable(speed=0)
time.sleep(2)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=re_di)
time.sleep(0.25)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=do_di)
time.sleep(0.75)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=re_di)
time.sleep(0.25)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=salt_di)
time.sleep(1.75)
CONV.enable(speed=0)
time.sleep(1)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=re_di)
time.sleep(0.25)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=0)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=re_di)
time.sleep(0.25)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=fa_di)
time.sleep(0.5)
CONV.enable(speed=0)
time.sleep(0.25)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=re_di)
time.sleep(0.25)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=0)
time.sleep(0.75)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=re_di)
time.sleep(0.25)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=fa_di)
time.sleep(0.5)
CONV.enable(speed=0)
time.sleep(0.25)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=re_di)
time.sleep(0.25)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=0)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=re_di)
time.sleep(0.25)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=fa_di)
time.sleep(0.5)
CONV.enable(speed=0)
time.sleep(0.25)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=re_di)
time.sleep(0.25)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=0)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.25)
CONV.enable(speed=re_di)
time.sleep(0.25)
CONV.enable(speed=la)
time.sleep(0.25)
CONV.enable(speed=salt_di)
time.sleep(0.5)
CONV.enable(speed=0)
time.sleep(1.25)
CONV.disable()
exit()
CONV.enable(speed=do)
time.sleep(0.5)
CONV.enable(speed=re)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=do)
time.sleep(0.25)
CONV.enable(speed=re)
time.sleep(0.5)
CONV.enable(speed=do)
time.sleep(0.25)
CONV.enable(speed=0)
time.sleep(1)
CONV.enable(speed=salt)
time.sleep(0.5)
CONV.enable(speed=fa)
time.sleep(0.5)
CONV.enable(speed=mi)
time.sleep(0.5)
CONV.enable(speed=re)
time.sleep(0.5)
CONV.enable(speed=do_di)
time.sleep(0.5)
CONV.enable(speed=do)
time.sleep(0.5)
CONV.disable()