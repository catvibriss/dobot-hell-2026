import asyncio
from objects.dobots import DobotDLL, DobotBLE
from config import *
from dataclasses import dataclass, field
from main import BASE_DOBOT, HELP_DOBOT, SORT_DOBOT

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

    def get_help_position(self, index: int):
        return [BUFFER_FPos_HELP[0], BUFFER_FPos_HELP[1] + (index * BUFFER_OFFSET), BUFFER_FPos_HELP[2]]
    
    def get_sort_position(self, index: int):
        return [BUFFER_FPos_SORT[0], BUFFER_FPos_SORT[1] - (index * BUFFER_OFFSET), BUFFER_FPos_SORT[2]]
    
    def allocate(self, cube: Cube) -> int:
        for i, occupied in enumerate(self.slots):
            if not occupied:
                self.slots[i] = True
                cube.buffer_place = i
                return i
        return -1
    
    def release(self, index: int):
        if 0 <= index < len(self.slots):
            self.slots[index] = False

BUFFER = Buffer(5)
sorting_queue: list[Cube] = []

def cube_sort_pos(color: int):
    box = BOXES[color]
    return box.get_next_position()

def sorting_move(cube: Cube):
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

    pick = None
    drop = cube_sort_pos(cube.color)

    asyncio.run(execute(pick, drop))
