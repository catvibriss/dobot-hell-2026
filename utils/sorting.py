from config import *
from main import BASE_ROBOT, SORT_ROBOT, HELP_ROBOT, CONV, DIST_SENSOR
from time import sleep

# boxes
BLUE_BOX = [False, False, False, False]
RED_BOX = [False, False, False, False] 
GREEN_BOX = [False, False, False, False] 
YELLOW_BOX = [False, False, False, False] 

work_queue = []

def start_sorting():
    count_of_cubes = int(input())
    for x in range(count_of_cubes, 0, -1):
        r = (x-1)//4
        c = (x-1)%4
        cpos = [BASE_LDPos[0] + BASE_X_OFFSET * c, BASE_LDPos[1] + BASE_Y_OFFSET * r]  
        BASE_ROBOT.move(x=cpos[0], y=cpos[1], z=BASE_CUBE_Z+2)
        BASE_ROBOT.set_suction_cup(True)
        BASE_ROBOT.move(relative=True, z=-3)
        BASE_ROBOT.move(z=25)
        BASE_ROBOT.move(x=CONV_BASE_3DPOS[0], y=CONV_BASE_3DPOS[1], z=CONV_BASE_3DPOS[2])
        BASE_ROBOT.set_suction_cup(False)
        sleep(0.1)
        BASE_ROBOT.move(relative=True, z=5)
        sleep(1)

def cube_sort_pos(color: int):
    box = []
    box_ldpos = [0, BOX_CONST_X]
    move_pos = []

    match color:
        case -1:
            return None
        case 0: # blue
            box = BLUE_BOX
            box_ldpos[0] = BLUE_BOX_LDPos
        case 3: # red
            box = RED_BOX
            box_ldpos[0] = RED_BOX_LDPos
        case 1: # green
            box = GREEN_BOX
            box_ldpos[0] = GREEN_BOX_LDPos
        case 2: # yellow
            box = YELLOW_BOX
            box_ldpos[0] = YELLOW_BOX_LDPos
    
    free_space_idx = box.index(False)
    match free_space_idx:
        case 0:
            move_pos = box_ldpos
        case 1:
            box_ldpos[0] += BOX_X_OFFSET
            move_pos = box_ldpos
        case 2:
            box_ldpos[1] -= BOX_Y_OFFSET
            move_pos = box_ldpos
        case 3:
            box_ldpos[0] += BOX_X_OFFSET
            box_ldpos[1] -= BOX_Y_OFFSET
            move_pos = box_ldpos
    
    box[free_space_idx] = True
    return move_pos

def reset_boxes():
    global BLUE_BOX, RED_BOX, GREEN_BOX, YELLOW_BOX
    BLUE_BOX = [False, False, False, False]
    RED_BOX = [False, False, False, False] 
    GREEN_BOX = [False, False, False, False] 
    YELLOW_BOX = [False, False, False, False] 

@DIST_SENSOR.on_change
def on_new_cube(value):
    print(value)