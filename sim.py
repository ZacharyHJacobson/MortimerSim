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

total_weight = 0
for task in tasks:
    total_weight += int(task[2])

superiors_count = 0
simming_task = False

def main():
    task_options = choose_task_options("Hydras", 100)
    for option in task_options:
        ticks_wasted = sim_ticks_wasted(get_task(option[0]), int(option[1]), int(option[2]))
        print(f"{option[0]} task with {option[1]} quantity and {option[2]}% more hearts wastes {ticks_wasted/HOUR} hours")

def choose_task_options(last_task: str, tasks_completed: int):
    task_options: list[list[str]]
    task_options = []
    for option in range(3 if tasks_completed >= 100 else 2):
        # choose task, can't be the previous task or one of the others on offer
        chosen_task = last_task
        while(chosen_task == last_task):
            task_by_weight = random.randrange(total_weight)
            for task in tasks:
                task_by_weight -= int(task[2])
                if(task_by_weight < 0):
                    #check if repeat
                    if(option != 0):
                        for previous_option in range(option):
                            if(task_options[previous_option][1] == task[1]):
                                break
                    chosen_task = task[1]
                    break
        # choose modifier
        modifiers_unlocked = 2
        if tasks_completed >= 25: modifiers_unlocked = 3
        if tasks_completed >= 50: modifiers_unlocked = 4
        if tasks_completed >= 75: modifiers_unlocked = 5
        task = get_task(chosen_task)
        modifier = random.randrange(modifiers_unlocked)
        #reroll modifier when clue scroll modifiers are impossible
        while(task[10] == "N/A" and modifier == 2):
            modifier = random.randrange(modifiers_unlocked)
        match(modifier):
            #slayer points
            case 0:
                task_options.append([chosen_task, "0", "0"])
            #task quantity
            case 1:
                if int(task[6]) < 0:
                    length_modifier = -random.randrange(-int(task[6]), (-int(task[7])) + 1)
                else:
                    length_modifier = random.randrange(int(task[6]), int(task[7]) + 1)
                task_options.append([chosen_task, length_modifier, "0"])
            #clue scrolls
            case 2:
                task_options.append([chosen_task, "0", "0"])
            #superior drop rate
            case 3:
                length_modifier = random.randrange(int(task[8]), int(task[9]) + 1)
                task_options.append([chosen_task, "0", "30"])
            #slayer xp
            case 4:
                task_options.append([chosen_task, "0", "0"])
    return task_options
            

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