import csv
from enum import Enum
import random

TASK_PREP_TIME = 30 # time to go back to Mortimer, choose task, restore stats if desired, and bank for new task
HOUR = 6000
class Bracelet(Enum):
    NONE = 1
    SLAUGHTER = 2
    EXPEDITIOUS = 3

with open("Mortimer.csv", mode="r") as file:
    tasks = list(csv.reader(file))[1:]

def main():
    print(calc_task_length("Hydras", 0, Bracelet.NONE))

def calc_task_length(task_name: str, length_modifier: int, bracelet: Bracelet):
    for task in tasks:
        if task[1] == task_name: 
            task_length = random.randrange(int(task[3]), int(task[4]) + 1)
            task_length += length_modifier
            match bracelet:
                case Bracelet.SLAUGHTER:
                    task *= 1.33
                case Bracelet.EXPEDITIOUS:
                    task *= .8
            return task_length
    raise NameError("task name not found")

if __name__ == '__main__':
    main()