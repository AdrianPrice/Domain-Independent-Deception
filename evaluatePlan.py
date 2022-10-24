import functools
from mimetypes import init
import re
from pyperplanmaster.src.pyperplan import grounding
from pyperplanmaster.src.run import plan
from pyperplanmaster.src.pyperplan.pddl.parser import Parser
from pyperplanmaster.src.pyperplan.planner import _parse, _ground, SEARCHES, HEURISTICS, search_plan
from pyperplanmaster.src.pyperplan.search.a_star import astar_search
from pyperplanmaster.src.pyperplan.search.breadth_first_search import breadth_first_search
from pyperplanmaster.src.pyperplan.heuristics.landmarks import *
from pyperplanmaster.src.pyperplan.heuristics.lm_cut import LmCutHeuristic
from pyperplanmaster.src.pyperplan.search.a_star import astar_search as astar_search_custom
from pyperplanmaster.src.pyperplan.heuristics.blind import *
import os
import shutil
import time
import subprocess
from csvOutputUtils import *

def evaluatePlan(realGoalTask, operations):
    task = realGoalTask
    optimalPath = breadth_first_search(task)
    optimalSteps = len(optimalPath)
    numberOfDeceptiveSteps = 0


    for op in operations:
        beforeSteps = len(optimalPath)
        task.initial_state = op.apply(task.initial_state)
        optimalPath = breadth_first_search(task)
        afterSteps = len(optimalPath)
        if beforeSteps != (afterSteps + 1):
            numberOfDeceptiveSteps += 1
    
    if optimalSteps == len(operations):
        return [len(operations), 0, 0]
    else:

        deceptionCost = (len(operations) - optimalSteps) / len(operations)
        deceptiveQuality = numberOfDeceptiveSteps / len(operations)
        deception = deceptiveQuality / deceptionCost
        return [deceptionCost, deceptiveQuality, deception]
    