import csv
from enum import Enum
import random

TASK_PREP_TIME = 30 # time to go back to Mortimer, choose task, restore stats if desired, and bank for new task
HOUR = 6000
SUPERIOR_RATE = 150
class Bracelet(Enum):
    NONE = 1
    SLAUGHTER = 2
    EXPEDITIOUS = 3

with open("Mortimer.csv", mode="r") as file:
    tasks = list(csv.reader(file))[1:]

superiors_count = 0

def main():
    task = get_task("Hydras")
    task_length = calc_task_length(task, 0, Bracelet.SLAUGHTER)
    task_count = 0
    time = 0
    got_heart = False
    while(got_heart == False):
        task_count += 1
        time += 3000
        got_heart = check_for_heart(task, task_length, 0)
    global superiors_count
    print(f"got heart in {task_count} tasks, {superiors_count} superiors, and {time/HOUR} hours")

def get_task(task_name):
    for task in tasks:
            if task[1] == task_name: return task
    raise NameError("task name not found")

def calc_task_length(task: list[str], length_modifier: int, bracelet: Bracelet):
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
    global superiors_count
    superiors_count += 1
    if(roll_for_heart(heart_chance)): return True
    while(drop_modifier >= 100):
        if(roll_for_heart(heart_chance)): return True
        drop_modifier -= 100
    if(random.randrange(0, 100) < drop_modifier):
        if(roll_for_heart(heart_chance)): return True
    return False

def roll_for_heart(heart_chance: int):
    return random.randrange(heart_chance) == 0

if __name__ == '__main__':
    main()