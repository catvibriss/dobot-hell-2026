import asyncio
from objects.dobots import DobotDLL, DobotBLE
from config import *
from dataclasses import dataclass
from main import BASE_DOBOT, HELP_DOBOT, SORT_DOBOT

BLUE_BOX    = [False, False, False, False]
RED_BOX     = [False, False, False, False] 
GREEN_BOX   = [False, False, False, False] 
YELLOW_BOX  = [False, False, False, False] 

@dataclass
class Cube:
    color: int
    conv_y_offset: float
    buffer_place: int = -1

BASE_DOBOT = BASE_DOBOT
HELP_DOBOT = HELP_DOBOT
SORT_DOBOT = SORT_DOBOT

buffer_places = []
sorting_queue: list[Cube] = []

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

def cube_sort_pos(color: int):
    box = []
    box_ldpos = [BOXES_X, 0]
    move_pos = []

    match color:
        case -1:
            return None
        case 0:
            box = RED_BOX
            box_ldpos[1] = RED_BOX_FPos
        case 1: 
            box = GREEN_BOX
            box_ldpos[1] = GREEN_BOX_FPos
        case 2:
            box = BLUE_BOX
            box_ldpos[1] = BLUE_BOX_FPos
        case 3: 
            box = YELLOW_BOX
            box_ldpos[1] = YELLOW_BOX_FPos
    
    free_space_idx = box.index(False)
    match free_space_idx:
        case 0:
            move_pos = box_ldpos
        case 1:
            box_ldpos[1] += BOX_L_OFFSET
            move_pos = box_ldpos
        case 2:
            box_ldpos[0] -= BOX_X_OFFSET
            move_pos = box_ldpos
        case 3:
            box_ldpos[0] -= BOX_X_OFFSET
            box_ldpos[1] += BOX_L_OFFSET
            move_pos = box_ldpos
    
    box[free_space_idx] = True
    return move_pos
