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

from approaches.BaselineApproach import BaselineApproach
from approaches.GoalToRealGoal import GoalToRealGoalApproach
from approaches.SharedLandmarks import SharedLandmarksApproach
from approaches.MostCommonLandmarks import MostCommonLandmarks
from approaches.CombinedLandmarks import CombinedLandmarksApproach

def landmarksForProblem(domainFile, problemFile): 
    '''
    Creates task files for each goal using the template,
    and uses these task files to extract landmarks.
    '''
    parser = Parser(domainFile, problemFile)
    dom = parser.parse_domain()
    problem = parser.parse_problem(dom)
    task = _ground(problem)

    extracted_landmarks_set = []
    landmark_type = '-factLandmarks'

    subprocess.call(['java', '-jar', 'libs/landmarks2.0.jar', domainFile, problemFile, landmark_type, os.path.join(TEMP_DIR, f'task-landmarks.txt')])

    with open(os.path.join(TEMP_DIR, f'task-landmarks.txt')) as landmarksFile:
        for line in landmarksFile:
            if 'fact' in landmark_type:
                for fact in task.facts:
                    if fact in line.rstrip():
                        extracted_landmarks_set.append(fact)
            elif 'action' in landmark_type:
                for op in task.operators:
                    if op.name in line.rstrip():
                        extracted_landmarks_set.append(op)
    return extracted_landmarks_set

def generatePlan(initialState, orderedLandmarks):
    def pathToGoal(acc, goal):
        task, ops = acc
        task.goals = goal
        heuristic = LandmarkHeuristic(task)
        path = breadth_first_search(task)
        
        for op in path:
            task.initial_state = op.apply(task.initial_state)
            ops.append(op)
        return acc

    acc = (initialState, [])
    return functools.reduce(pathToGoal, orderedLandmarks, acc)

def getRealTask():
    """ Get real task """
    realProblemFile = os.path.join(TEMP_DIR, f"task-real.pddl")
    realTask = template.replace("<HYPOTHESIS>", realGoal)

    with open(realProblemFile, "w") as create:
                create.write(realTask)
    
    parser = Parser(os.path.abspath(domaindir), realProblemFile)
    dom = parser.parse_domain()
    problem = parser.parse_problem(dom)
    return _ground(problem)

if __name__ == "__main__":
    DIR = os.path.dirname(__file__)
    # Defining constants
    EXPERIMENTS_DIR = os.path.join(DIR, 'experiment-data/experiment-input')
    TEMP_DIR = os.path.join(DIR, 'temp')

    for _, dirs, _ in os.walk(EXPERIMENTS_DIR):
        for dname in dirs:
            print(f"Starting domain {dname}")
            domaindir = f"{EXPERIMENTS_DIR}/{dname}/domain.pddl"
            hypsdir = f"{EXPERIMENTS_DIR}/{dname}/hyps.dat"
            realhypdir = f"{EXPERIMENTS_DIR}/{dname}/real_hyp.dat"
            templatedir = f"{EXPERIMENTS_DIR}/{dname}/template.pddl"

            """ Generate output files """
            OUTPUT_DIR = os.path.join(
                DIR, f"experiment-data/experiment-output/{dname}")
            if os.path.exists(OUTPUT_DIR):
                shutil.rmtree(OUTPUT_DIR)

            os.mkdir(OUTPUT_DIR)

            """ Create CSV outputs """
            domainOutput = CSVDomainOutput(OUTPUT_DIR)
            approachOutput = CSVApproachOutput(OUTPUT_DIR)

            """ Get real goal """
            with open(realhypdir) as realGoalFile:
                realGoal = realGoalFile.read().lower().rstrip('\n')
                realGoalFile.close()
            
            """ Read template"""
            with open(templatedir) as templatefile:
                template = templatefile.read()
                templatefile.close()
            
            """ Run vanilla pyperplan """
            _ = getRealTask() # This is to just ensure the real problem file has been created
            realProblemFile = os.path.join(TEMP_DIR, f"task-real.pddl")
            vanillaOutput = approachOutput.addNewRow()
            vanillaOutput.approachName = "Vanilla Pyperplan"

            print("Running vanilla pyperplan")
            vanillaGenerationStart = time.time()
            ops = search_plan(domaindir, realProblemFile, SEARCHES["bfs"], None)
            vanillaGenerationEnd = time.time()
            
            vanillaOutput.planTime = vanillaGenerationEnd - vanillaGenerationStart
            vanillaOutput.path = ops
            vanillaOutput.pathLength = len(ops)
            vanillaOutput.initialState = getRealTask().initial_state
            vanillaOutput.goalState = getRealTask().goals

            """ Extract landmarks """      
            extractedLandmarks = {}
            with open(hypsdir) as hyps:
                for index, goal in enumerate(hyps.readlines()):
                    goal = goal.lower().rstrip('\n')

                    csvOutputRow = domainOutput.addNewRow()
                    csvOutputRow.domainName = dname
                    csvOutputRow.goalState = goal
                    csvOutputRow.isRealGoal = goal == realGoal
                    csvOutputRow.initialState = getRealTask().initial_state

                    problemFile = os.path.join(TEMP_DIR, f"task{index}.pddl")
                    problem = template.replace("<HYPOTHESIS>", goal)

                    with open(problemFile, "w") as create:
                        create.write(problem)

                    extractLandmarkStart = time.time()
                    landmarks = landmarksForProblem(os.path.abspath(domaindir), problemFile)
                    extractLandmarkEnd = time.time()

                    csvOutputRow.extractionTime = extractLandmarkEnd - extractLandmarkStart
                    csvOutputRow.landmarks = landmarks

                    extractedLandmarks[goal] = landmarks
                hyps.close()


            """ Generate deceptive plans """
            approaches = [BaselineApproach, GoalToRealGoalApproach, SharedLandmarksApproach, CombinedLandmarksApproach, MostCommonLandmarks]

            for approachObj in approaches:
                csvApproachRow = approachOutput.addNewRow()
                approach = approachObj(extractedLandmarks, getRealTask(), realGoal)
                csvApproachRow.approachName = approach.NAME
                print(f"Running approach {approach.NAME}")

                parser = Parser(os.path.abspath(domaindir), os.path.join(TEMP_DIR, f"task0.pddl"))
                dom = parser.parse_domain()
                problem = parser.parse_problem(dom)
                task = _ground(problem)

                """ Order landmarks"""
                orderingLandmarksStart = time.time()
                orderedLandmarks = approach.generate()
                orderingLandmarksEnd = time.time()

                """ Generate plan """
                generatePlanStart = time.time()
                plan = generatePlan(getRealTask(), orderedLandmarks)
                generatePlanEnd = time.time()

                """ Log results"""
                csvApproachRow.initialState = getRealTask().initial_state
                csvApproachRow.goalState = orderedLandmarks[-1]
                csvApproachRow.orderingTime = orderingLandmarksEnd - orderingLandmarksStart
                csvApproachRow.planTime = generatePlanEnd - generatePlanStart
                csvApproachRow.pathLength = len(plan[1])
                csvApproachRow.path = plan[1]


            """ Output results"""
            domainOutput.writeToCSV(f"{dname}")
            approachOutput.writeToCSV(f"{dname}-approaches")
