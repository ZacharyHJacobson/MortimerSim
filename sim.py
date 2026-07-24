import csv
from enum import Enum
import random

TASK_PREP_TIME = 30 # time to go back to Mortimer, choose task, restore stats if desired, and bank for new task
HOUR = 6000
SUPERIOR_RATE = 150
SIMS_PER_TASK = 10000
HEARTS_SIMULATED = 10000
TIME_PER_HEART = 70 * HOUR
class Bracelet(Enum):
    NONE = 1
    SLAUGHTER = 2
    EXPEDITIOUS = 3

with open("Mortimer.csv", mode="r") as file:
    tasks = list(csv.reader(file))[1:]

superiors_count = 0
simming_task = False

def main():
    task = get_task("Hydras")
    ticks_wasted = sim_ticks_wasted(task, 0, 150)
    print(f"task wastes {ticks_wasted/HOUR} hours")

def sim_ticks_wasted(task: list[str], length_modifier: int, drop_modifier: int):
    global simming_task
    simming_task = True

    task_completion_time = TASK_PREP_TIME + int(task[17])
    task_completion_time += calc_task_length(task, length_modifier, Bracelet.SLAUGHTER, True)
    total_time = 0
    for sim in range(SIMS_PER_TASK):
        task_length = calc_task_length(task, length_modifier, Bracelet.SLAUGHTER, False)
        got_heart = False
        while(got_heart == False):
            total_time += TASK_PREP_TIME
            total_time += int(task[17])
            total_time += int((float(task_length) / int(task[18])) * HOUR)
            got_heart = check_for_heart(task, task_length, drop_modifier)

    task_time_per_heart = total_time / SIMS_PER_TASK

    simming_task = False
    return(task_completion_time * (1-(TIME_PER_HEART/task_time_per_heart)))


def get_task(task_name: str):
    for task in tasks:
            if task[1] == task_name: return task
    raise NameError("task name not found")

# number of monsters to kill per task
def calc_task_length(task: list[str], length_modifier: int, bracelet: Bracelet, average: bool):
    if(average):
        task_length = (int(task[4]) + int(task[3]))/2
    else:
        task_length = random.randrange(int(task[3]), int(task[4]) + 1)
    task_length += length_modifier
    match bracelet:
        case Bracelet.SLAUGHTER:
            task_length += int(task_length / 3)
        case Bracelet.EXPEDITIOUS:
            task_length -= int(task_length / 5)
    return task_length

def check_for_heart(task: list[str], task_length: int, drop_modifier: int):
    heart_chance = int(task[16])
    # no reason to randomize superiors until remainder, so one superior every on-rate until then
    while(task_length >= SUPERIOR_RATE):
        if(spawn_superior(heart_chance, drop_modifier)): return True
        task_length -= SUPERIOR_RATE
    if(random.randrange(0, SUPERIOR_RATE) < task_length):
        if(spawn_superior(heart_chance, drop_modifier)): return True
    return False

def spawn_superior(heart_chance: int, drop_modifier: int):
    increment_superiors()
    heart_chance = int((heart_chance * 100) / (100 + drop_modifier))
    return(random.randrange(heart_chance) == 0)

def increment_superiors():
    global simming_task
    if(not simming_task):
       global superiors_count
       superiors_count += 1
    

if __name__ == '__main__':
    main()