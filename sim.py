import csv
import configparser
from enum import IntEnum
import random

HOUR = 6000
Bracelet = IntEnum("Bracelet", ["NONE", "SLAUGHTER", "EXPEDITIOUS"])

with open("Mortimer.csv", mode="r") as mfile:
    tasks = list(csv.reader(mfile))[1:]
Stats = IntEnum("Stats", ["SLAYER_LEVEL", "CREATURE", "WEIGHTING", "ASSIGN_MIN", "ASSIGN_MAX", "EXTENDABLE", "QUANTITY_MIN", "QUANTITY_MAX", "POINTS_MIN", "POINTS_MAX", "CLUE_MIN", "CLUE_MAX", "XP_MIN", "XP_MAX", "DROP_MIN", "DROP_MAX", "HEART_DENOMINATOR", "TRAVEL_TIME", "KILLS_PER_HOUR", "NORMAL_EXPERIENCE", "SUPERIOR_EXPERIENCE"], start=0)

config = configparser.ConfigParser()
config.read("config.ini")
TASK_PREP_TIME = config.getint("settings", "task_prep_time") # time to go back to Mortimer, choose task, restore stats if desired, and bank for new task
SUPERIOR_RATE = config.getint("settings", "superior_rate")
HEARTS_SIMULATED = config.getint("settings", "hearts_simulated")
TIME_PER_HEART = config.getfloat("settings", "time_per_heart")
SLAYER_CAPE = config.getboolean("settings", "slayer_cape")
BLOCKS = [config["settings"]["block1"],config["settings"]["block2"]]

total_weight = 0
for t in tasks:
    total_weight += int(t[Stats.WEIGHTING])

xp_boost = 0.0

def main():
    total_time_taken = 0
    for _ in range(HEARTS_SIMULATED):
        total_time_taken += sim_until_heart()
    print(f"total time taken: {total_time_taken}")
    print(f"time taken per heart: {total_time_taken/HEARTS_SIMULATED}")
    print(f"in hours: {total_time_taken/HEARTS_SIMULATED/HOUR}")


def sim_until_heart():
    got_heart = False
    time_elapsed = 0
    last_task_name = "None"
    tasks_completed = 0
    while(got_heart == False):
        task_options = choose_task_options(last_task_name, tasks_completed)
        task_ratings = []
        for option in task_options:
            ticks_wasted = calc_ticks_wasted(get_task(option[0]), int(option[1]), int(option[2]))
            task_ratings.append(ticks_wasted)
        best_option = task_ratings.index(min(task_ratings))
        last_task_name = task_options[best_option][0]
        best_task = get_task(last_task_name)
        above_average = task_ratings[best_option] < 0
        if(above_average):
            task_length = kills_per_task(best_task, int(task_options[best_option][1]), Bracelet.SLAUGHTER, False)
        else:
            task_length = kills_per_task(best_task, int(task_options[best_option][1]), Bracelet.EXPEDITIOUS, False)
        added_time = time_per_task(best_task, task_length)
        global xp_boost
        xp_boost = 0.0
        if(task_options[best_option][3] == 7):
            xp_boost = float(int(best_task[Stats.XP_MIN].split(".")[0]) + int(best_task[Stats.XP_MAX].split(".")[0]))/200.0
        first_completion = True
        while(first_completion or (above_average and SLAYER_CAPE and (random.randrange(10) == 0) and not got_heart)):
            time_elapsed += added_time
            got_heart = check_task_for_heart(best_task, task_length, int(task_options[best_option][2]))
            tasks_completed += 1

            first_completion = False
    return(time_elapsed)
    

def choose_task_options(last_task_name: str, tasks_completed: int):
    task_options: list[list[str]]
    task_options = []
    for option in range(3 if tasks_completed >= 50 else 2):
        # choose task, can't be the previous task or one of the others on offer
        chosen_task_name = last_task_name
        while(chosen_task_name == last_task_name):
            task_by_weight = random.randrange(total_weight)
            for task in tasks:
                task_by_weight -= int(task[Stats.WEIGHTING])
                if(task_by_weight < 0):
                    #check if repeat
                    if(option != 0):
                        for previous_option in range(option):
                            if(task_options[previous_option][1] == task[Stats.CREATURE]):
                                break
                    #check if blocked
                    if((BLOCKS[0] == task[Stats.CREATURE]) or (BLOCKS[1] == task[Stats.CREATURE])):
                        break
                    chosen_task_name = task[Stats.CREATURE]
                    break
        # choose modifier
        modifiers_unlocked = 2
        if tasks_completed >= 15: modifiers_unlocked = 3
        if tasks_completed >= 25: modifiers_unlocked = 4
        if tasks_completed >= 40: modifiers_unlocked = 5
        task = get_task(chosen_task_name)
        modifier = random.randrange(modifiers_unlocked)
        #reroll modifier when clue scroll modifiers are impossible
        while(task[Stats.CLUE_MIN] == "N/A" and modifier == 2):
            modifier = random.randrange(modifiers_unlocked)
        match(modifier):
            #slayer points
            case 0:
                task_options.append([chosen_task_name, "0", "0", 3])
            #task quantity
            case 1:
                if int(task[Stats.QUANTITY_MIN]) < 0:
                    length_modifier = -random.randrange(-int(task[Stats.QUANTITY_MIN]), (-int(task[Stats.QUANTITY_MAX])) + 1)
                else:
                    length_modifier = random.randrange(int(task[Stats.QUANTITY_MIN]), int(task[Stats.QUANTITY_MAX]) + 1)
                task_options.append([chosen_task_name, length_modifier, "0", 4])
            #clue scrolls
            case 2:
                task_options.append([chosen_task_name, "0", "0", 5])
            #superior drop rate
            case 3:
                min = int(task[Stats.DROP_MIN].split(".")[0])
                max = int(task[Stats.DROP_MAX].split(".")[0])
                superior_modifier = 5 * random.randrange(int(min/5), int(max/5) + 1)
                task_options.append([chosen_task_name, "0", superior_modifier, 6])
            #slayer xp
            case 4:
                task_options.append([chosen_task_name, "0", "0", 7])
    return task_options

def calc_ticks_wasted(task: list[str], length_modifier: int, drop_modifier: int, bracelet=Bracelet.EXPEDITIOUS):
    task_length = kills_per_task(task, length_modifier, bracelet, True)
    task_completion_time = time_per_task(task, task_length)
    tasks_per_heart = count_tasks_for_heart(task, task_length, drop_modifier)
    task_time_per_heart = task_completion_time * tasks_per_heart
    if(task_time_per_heart < TIME_PER_HEART and bracelet == Bracelet.EXPEDITIOUS):
        return calc_ticks_wasted(task, length_modifier, drop_modifier, Bracelet.SLAUGHTER)

    return(task_completion_time * (1-(TIME_PER_HEART/task_time_per_heart)))

def time_per_task(task: list[str], task_length: int):
    time = TASK_PREP_TIME + int(task[Stats.TRAVEL_TIME])
    time += int(task_length / float(task[Stats.KILLS_PER_HOUR]) * HOUR)
    return(time)


def get_task(task_name: str):
    for task in tasks:
            if task[Stats.CREATURE] == task_name: return task
    raise NameError("task name not found")

def kills_per_task(task: list[str], length_modifier: int, bracelet: Bracelet, average: bool):
    if(average):
        task_length = (int(task[Stats.ASSIGN_MIN]) + int(task[Stats.ASSIGN_MAX]))/2
    else:
        task_length = random.randrange(int(task[Stats.ASSIGN_MIN]), int(task[Stats.ASSIGN_MAX]) + 1)
    task_length += length_modifier
    match bracelet:
        case Bracelet.SLAUGHTER:
            task_length += int(task_length / 3)
        case Bracelet.EXPEDITIOUS:
            task_length -= int(task_length / 5)
    return task_length

def count_tasks_for_heart(task: list[str], task_length: int, drop_modifier: int):
    superiors_per_task = task_length/SUPERIOR_RATE
    superiors_per_heart = (int(task[Stats.HEART_DENOMINATOR]) * 100.0) / (100.0 + drop_modifier)
    return superiors_per_heart/superiors_per_task

def check_task_for_heart(task: list[str], task_length: int, drop_modifier: int):
    num_superiors = int(task_length/SUPERIOR_RATE)
    if(random.randrange(0, SUPERIOR_RATE) < task_length%SUPERIOR_RATE): num_superiors += 1
    for _ in range(num_superiors):
        if(roll_superior_heart_chance(int(task[Stats.HEART_DENOMINATOR]), drop_modifier)): return True
    return False

def roll_superior_heart_chance(heart_chance: int, drop_modifier: int):
    modified_chance = int((heart_chance * 100) / (100 + drop_modifier))
    return(random.randrange(modified_chance) == 0)

if __name__ == '__main__':
    main()