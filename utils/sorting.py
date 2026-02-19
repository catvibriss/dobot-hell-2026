import asyncio
from objects.dobots import DobotDLL, DobotBLE
from config import *
from dataclasses import dataclass, field
from main import BASE_DOBOT, HELP_DOBOT, SORT_DOBOT
import time
import random

@dataclass
class Cube:
    color: int
    conv_y_offset: float
    buffer_place: int = -1

@dataclass
class Box:
    color: int
    slots: list[bool] = field(default_factory=lambda: [False, False, False, False])
    base_y: float = 0.0
    
    def get_next_position(self) -> list[float]:
        if False not in self.slots:
            return None
        
        idx = self.slots.index(False)
        
        pos_x = BOXES_X
        pos_l = self.base_y
        
        match idx:
            case 1:
                pos_l += BOX_L_OFFSET
            case 2:
                pos_x -= BOX_X_OFFSET
            case 3:
                pos_x -= BOX_X_OFFSET
                pos_l += BOX_L_OFFSET
    
        self.slots[idx] = True        
        return [pos_x, pos_l, BOXES_Z_CUBE]

BOXES = {0: Box(color=0, base_y=RED_BOX_FPos),
         1: Box(color=1, base_y=GREEN_BOX_FPos),
         2: Box(color=2, base_y=BLUE_BOX_FPos),
         3: Box(color=3, base_y=YELLOW_BOX_FPos)}

class Buffer:
    def __init__(self, slots: int):
        self.slots = [False] * slots
        self._lock = asyncio.Lock()

    def get_help_position(self, index: int):
        return [BUFFER_FPos_HELP[0], BUFFER_FPos_HELP[1] + (index * BUFFER_OFFSET), BUFFER_FPos_HELP[2]]
    
    def get_sort_position(self, index: int):
        return [BUFFER_FPos_SORT[0], BUFFER_FPos_SORT[1] - (index * BUFFER_OFFSET), BUFFER_FPos_SORT[2]]
    
    async def allocate(self, cube: Cube) -> int:
        async with self._lock:
            for i, occupied in enumerate(self.slots):
                if not occupied:
                    self.slots[i] = True
                    cube.buffer_place = i
                    return i
            return -1
    
    async def release(self, index: int):
        async with self._lock:
            if 0 <= index < len(self.slots):
                self.slots[index] = False

BUFFER = Buffer(4)
sorting_queue: list[Cube] = []

def cube_sort_pos(color: int):
    box = BOXES[color]
    return box.get_next_position()

async def sorting_move(cube: Cube):
    """
    place cords = [x, l, z] (l equal y for sort rail)
    """
    worker = SORT_DOBOT

    async def execute(pick_place, drop_place) -> None:
        await worker.set_suction_cup(False)
        await worker.move(z=0)
        await worker.move(x=pick_place[0], l=pick_place[1])
        await worker.move(z=pick_place[2]+5)
        await worker.set_suction_cup(True)
        await worker.move(z=pick_place[2]-2)
        await worker.move(relative=True, z=35)
        await worker.move(x=drop_place[0], l=drop_place[1])
        await worker.move(z=drop_place[2])
        await worker.set_suction_cup(False)
        await worker.move(relative=True, z=5)

        await BUFFER.release(cube.buffer_place)

    pick = BUFFER.get_sort_position(cube.buffer_place)
    drop = cube_sort_pos(cube.color)

    await execute(pick, drop)

# when camera register new cube
# @camera -> color, offset
def new_cube(color: int, offset: float):
    cube = Cube(color=color, conv_y_offset=offset)
    sorting_queue.append(cube)

# when OS get obstacle 
# @obstacle -> None
async def sort_cube():
    current_cube = sorting_queue[0]

    help_worker: DobotDLL = None#HELP_DOBOT
    
    # готов поймать
    help_worker.move(z=CONV_HELP_3DPOS[2]+30, r=0)
    help_worker.move(x=CONV_HELP_3DPOS[0], y=CONV_HELP_3DPOS[1]+current_cube.conv_y_offset)
    help_worker.set_gripper("open")
    help_worker.set_gripper("off")
    help_worker.move(z=CONV_HELP_3DPOS[2])

    # поймал
    await asyncio.sleep(CONV_IFS_SLEEP_TIME)
    help_worker.set_gripper("close")
    await BUFFER.allocate(current_cube)

    # передвинул в буфер
    buffer_cords = BUFFER.get_help_position(current_cube.buffer_place)
    help_worker.set_gripper("off")
    help_worker.move(x=buffer_cords[0], y=buffer_cords[1], z=buffer_cords[2], r=90)
    help_worker.set_gripper("on")
    await asyncio.sleep(0.6)
    help_worker.set_gripper("off")
    
    # отодвинулся для сортировки
    help_worker.move(relative=True, z=30, x=-45, y=-45)

    sorting_queue.pop(0)
    # передал сортировке
    await sorting_move(current_cube)

def place_from_base(base_index: int):
    """
    index of base (short example):
    [0, 1
    2, 3]
    """
    worker = BASE_DOBOT

    row = (base_index)//4
    column = (base_index)%4
    cube_x = BASE_FPos[0] + BASE_X_OFFSET * column
    cube_y = BASE_FPos[1] - BASE_Y_OFFSET * row
    worker.move(x=cube_x, y=cube_y, z=BASE_Z_PLACE+2)
    worker.set_suction_cup(True)
    worker.move(relative=True, z=-3)
    worker.move(z=25)
    worker.move(x=CONV_BASE_3DPOS[0], y=CONV_BASE_3DPOS[1], z=CONV_BASE_3DPOS[2])
    worker.set_suction_cup(False)
    worker.move(relative=True, z=5)

def start_sorting(randomize: bool = False):
    indexes = list(range(16))
    if randomize:
        random.shuffle(indexes)

    for idx in indexes:
        place_from_base(idx)
        time.sleep(2)

