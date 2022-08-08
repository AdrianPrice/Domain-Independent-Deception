import functools
import re
from pyperplanmaster.src.pyperplan import grounding
from pyperplanmaster.src.pyperplan.pddl.parser import Parser
from pyperplanmaster.src.pyperplan.planner import _parse, _ground
from pyperplanmaster.src.pyperplan.search.a_star import astar_search
from pyperplanmaster.src.pyperplan.heuristics.landmarks import *
from pyperplanmaster.src.pyperplan.heuristics.lm_cut import LmCutHeuristic
from pyperplanmaster.src.pyperplan.search.a_star import astar_search as astar_search_custom
from pyperplanmaster.src.pyperplan.heuristics.blind import *
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import math
import argparse
import shutil
import csv
import time

class CSVApproachOutput():
    def __init__(self) -> None:
        self.rows = []
        self.header = ["Approach", "Initial", "Goal", "Time to Generate Plan", "Path Length", "Path", "Deceptive Stats (Is step truthful, Steps to Goal)", "Extra Cost Ratio", "Extra Deceptiveness Ratio"]
    
    def addNewRow(self):
        row = CSVApproachRow()
        self.rows.append(row)
        return row
    
    def writeToCSV(self, filename):
        f = open(os.path.join(os.path.dirname(__file__),
                                  OUTPUT_DIR) + f"/{filename}.csv", "a")
        writer = csv.writer(f)
        writer.writerow(self.header)
        for row in self.rows:
            writer.writerow(row.dataToWrite())
        f.close()

class CSVApproachRow():
    def __init__(self) -> None:
        self.approachName = "not provided"
        self.initialState = "not provided"
        self.goalState = "not provided"
        self.time = -1
        self.pathLength = -1
        self.path = "not provided"
        self.deceptiveStats = "not collected (use --deceptivestats to see this value)"
        self.extraCost = "not collected (use --deceptivestats to see this value)"
        self.extraDeceptiveness = "not collected (use --deceptivestats to see this value)"

    
    def dataToWrite(self):
        return [self.approachName, self.initialState, self.goalState, self.time, self.pathLength, self.path, self.deceptiveStats, self.extraCost, self.extraDeceptiveness]

class CSVDomainOutput():
    def __init__(self) -> None:
        self.rows = []
        self.header = ["Domain Name", "Potential Goal", "Initial", "isRealGoal", "Time to Extract Landmarks", "Extracted Landmarks"]
    
    def addNewRow(self):
        row = CSVDomainRow()
        self.rows.append(row)
        return row
    
    def writeToCSV(self, filename):
        f = open(os.path.join(os.path.dirname(__file__),
                                  OUTPUT_DIR) + f"/{filename}.csv", "a")
        writer = csv.writer(f)
        writer.writerow(self.header)
        for row in self.rows:
            writer.writerow(row.dataToWrite())
        f.close()
        
class CSVDomainRow():
    def __init__(self) -> None:
        self.domainName = "not provided"
        self.goalState = "not provided"
        self.initialState = "not provided"
        self.isRealGoal = False
        self.extractionTime = -1
        self.landmarks = "not provided"
    
    def dataToWrite(self):
        return [self.domainName, self.goalState, self.initialState, self.isRealGoal, self.extractionTime, self.landmarks]


def verbosePrint(*data):
    if argparser.parse_args().verbose:
        output = ""
        for element in data:
            output += str(element)
        print(output)


class ExtractLandmarks():
    '''
    self.domainFile - location of the domain file
    self.taskTemplate - template of task pddl file

    self.goals - list of goals
    self.realGoalIndex - the actual goal
    self.landmarks - list of landmarks generated from goals

    self.debug - whether to #print debug comments
    '''
    #################
    ### VARIABLES ###
    #################
    TEMP_DIR = os.path.join(os.path.dirname(__file__),
                            "temp")  # Location of temp folder

    ###################################
    ### INITIALIZATION OF LANDMARKS ###
    ###################################
    def __init__(self, *args, debug=False) -> None:
        '''
        Constructs landmarks out of given domain file, goals list and task template pddl.
        '''
        self.debug = debug
        self.landmarks = []
        self.ordering = []
        self.initialTask = None
        if len(args) == 1:
            pass
            # self.__unpackTar(*args)
        elif len(args) == 4:
            self.__unpackFiles(*args)
        else:
            raise TypeError("Incorrect number of arguments.")
        self.optimal_plans = self.generate_optimal()

    def __unpackFiles(self, domaindir, hypsdir, realhypdir, templatedir) -> None:
        '''
        Loads the necessary resources into class variables. This function is called when
        three arguments are given.
        '''
        verbosePrint(f"##### Getting landmarks #####")
        self.domainFile: str = os.path.abspath(domaindir)
        with open(hypsdir) as goalsfile:
            self.goals: list[str] = goalsfile.read().splitlines()
        with open(realhypdir) as realhypfile:
            self.realGoalIndex: int = self.goals.index(realhypfile.readline())
        with open(templatedir) as templatefile:
            self.taskTemplate: str = templatefile.read()

        # DEBUG
        verbosePrint('# List of Goals parsed: #\n',
                     *[f"{i} : {a}\n" for i, a in enumerate(self.goals)])
        verbosePrint('# Real Goal parsed: #\n',
                     f"{self.realGoalIndex} : {self.goals[self.realGoalIndex]}\n")

        self.__populate()

    def __populate(self) -> None:
        '''
        Creates task files for each goal using the template,
        and uses these task files to extract landmarks.
        '''
        for i in range(len(self.goals)):
            dirname = self.tempLoc(f"task{i}.pddl")
            task = self.taskTemplate.replace("<HYPOTHESIS>", self.goals[i])
            with open(dirname, "w") as create:
                create.write(task)
            parser = Parser(self.domainFile, dirname)
            dom = parser.parse_domain()
            problem = parser.parse_problem(dom)
            task = _ground(problem)
            # verbosePrint(task)
            if self.initialTask == None:
                self.initialTask = task
            landmarks, self.landmark_ordering = get_landmarks(task, True)
            landmarks_set = list(map(self.parse_goal, landmarks))
            self.landmarks.append(landmarks_set)

        verbosePrint('# List of Landmarks calculated:\n',
                     * [f"{i} : {self.goals[i]} : {a}\n" for i, a in enumerate(self.landmarks)])

    def tempLoc(self, name):
        ''' Returns an absolute directory to the temp location.
        '''
        return os.path.join(self.TEMP_DIR, name)

    def parse_goal(self, goal):
        verbosePrint("parsing ", goal)
        parsedgoals = re.findall('\([A-Za-z0-9 ]*\)', goal)
        verbosePrint("parsed", parsedgoals)
        return parsedgoals

    def generate_optimal(self):
        optimal_paths = []
        goal_task = _ground(
            _parse(self.domainFile, self.tempLoc("task0.pddl")))
        for goal in self.goals:
            verbosePrint(f"Calculating OPTIMAL...")
            verbosePrint(goal)
            goal_task.goals = self.parse_goal(goal)
            heuristic = LmCutHeuristic(goal_task)
            goal_plan = astar_search(goal_task, heuristic)
            optimal_paths.append(len(goal_plan))
            verbosePrint(f"Calculated length: {len(goal_plan)}")
        return optimal_paths

    def getRealGoal(self, parse=False):
        return self.getGoal(self.realGoalIndex, parse)

    def getGoal(self, index, parse=False):
        goal = self.goals[index]
        return self.parse_goal(goal) if parse else goal

    def getRealLandmark(self, parse=False):
        return self.getLandmark(self.realGoalIndex, parse)

    def getLandmark(self, index, parse=False):
        landmark = self.landmarks[index]
        return self.parse_goal(landmark) if parse else landmark


class ApproachTemplate():
    def __init__(self, extractedLandmarks: ExtractLandmarks):
        self.l = extractedLandmarks

    def generate(self):
        pass


class BaselineApproach(ApproachTemplate):
    NAME = "Baseline Approach"
    DESCRIPTION = """
    Calculates a path from the initial state to the real goal.
    """

    def __init__(self, extractedLandmarks: ExtractLandmarks):
        super().__init__(extractedLandmarks)

    def generate(self):
        ordered_l = []
        ordered_l.append(self.l.getRealGoal(True))
        return ordered_l


class GoalToRealGoalApproach(ApproachTemplate):
    NAME = "Goal to Real Goal Approach"
    DESCRIPTION = """
    Calculates a path from the initial state to a candidate goal which has the
    most landmarks in common with the real goal.
    """

    def __init__(self, extractedLandmarks: ExtractLandmarks):
        super().__init__(extractedLandmarks)

    def generate(self):
        '''
        Method for picking landmarks:
            - The goal with the most landmarks in common with the real goal is the most in common.
        '''
        def intersection(lst1, lst2):
            lst3 = [value for value in lst1 if value in lst2]
            return lst3

        landmarkIntersection = [intersection(i,
                                             self.l.getRealLandmark()) for i in self.l.landmarks]
        # Intersection with self to empty set
        landmarkIntersection[self.l.realGoalIndex] = {}
        # verbosePrint(
        # "# Intersection of goals with the real goal",
        # *[f"{i}: {a} " if i != self.l.realGoalIndex else "" for i, a in enumerate(landmarkIntersection)])
        # verbosePrint(landmarkIntersection)
        landmarkSetIndex = landmarkIntersection.index(
            max(landmarkIntersection, key=len))  # Result has a list of landmarks
        verbosePrint(
            "# The index of the goal with the largest number of landmarks in common",
            landmarkSetIndex)

        ordered_l = []
        ordered_l.append(self.l.getGoal(landmarkSetIndex, True))
        ordered_l.append(self.l.getRealGoal(True))
        return ordered_l


class OldScoringApproach(ApproachTemplate):
    NAME = "Old Scoring Approach"
    DESCRIPTION = """
        Travels to each landmark which is ordered by the number of "sub landmarks" it covers
        """

    def __init__(self, extractedLandmarks: ExtractLandmarks):
        super().__init__(extractedLandmarks)

    def generate(self):
        '''
        Method for picking landmarks:
            - The goal with the most landmarks in common with the real goal is the most in common.

        Method for ordering landmarks:
            - This goal's landmarks are ordered based on similiarity to the initial state.
        '''
        def ordering_score(landmark):
            ''' Order landmarks based on similiarity to the initial task '''
            initialTask = self.l.initialTask
            initialTask.goals = landmark
            # get the landmarks of this landmark
            landmarks = get_landmarks(initialTask)
            verbosePrint(f"LANDMARKS:{landmark} : {landmarks}")
            verbosePrint(f"Landmark: {landmark}, Score: {len(landmarks)}")
            return len(landmarks)

        # PICKING LANDMARKS
        def intersection(lst1, lst2):
            lst3 = [value for value in lst1 if value in lst2]
            return lst3

        landmarkIntersection = [intersection(i,
                                             self.l.getRealLandmark()) for i in self.l.landmarks]
        # Intersection with self to empty set
        landmarkIntersection[self.l.realGoalIndex] = {}
        verbosePrint(
            "# Intersection of goals with the real goal",
            *[f"{i}: {a} " if i != self.l.realGoalIndex else "" for i, a in enumerate(landmarkIntersection)])

        # Result has a list of landmarks
        landmarkSet = max(landmarkIntersection, key=len)
        verbosePrint(
            "# The intersection with the largest number of landmarks",
            *[f"{i}: {a} " for i, a in enumerate(landmarkSet)])

        # LANDMARK ORDERING
        verbosePrint(f"# Sorting based on score")
        verbosePrint(landmarkSet)
        ordered_l = sorted(
            landmarkSet, key=lambda landmark: ordering_score(landmark))
        verbosePrint(f"Sorted based on score: {ordered_l}")
        ordered_l.append(self.l.getRealGoal(True))
        return ordered_l


class NewScoringApproach(ApproachTemplate):
    NAME = "New Scoring Approach"
    DESC = """
    Travels to each landmark which is ordered by the number of "sub landmarks" it covers
    """

    def __init__(self, extractedLandmarks: ExtractLandmarks):
        super().__init__(extractedLandmarks)

    def generate(self):
        mem_dict = {}
        # PICKING LANDMARKS

        def ordering_score(landmark, foundLandmarks=[]):
            verbosePrint("F", foundLandmarks)
            ''' Order landmarks based on similiarity to the initial task '''
            core = mem_dict.get(frozenset(landmark))
            verbosePrint(landmark, score)
            if not score:
                # calculate score if it isnt already in the dictionary
                initialTask = self.l.initialTask
                initialTask.goals = landmark
                # get the landmarks of this landmark
                landmarks = get_landmarks(initialTask)
                verbosePrint(landmarks, set(landmark).issubset(set(landmarks)))
                if set(landmark).issubset(set(landmarks)):
                    for l in landmark:
                        verbosePrint("removed ", l)
                        landmarks.remove(l)
                foundLandmarks.append(landmark)
                verbosePrint("L", landmarks)
                for l in landmarks:
                    # verbosePrint("HI", [l], landmarks)
                    if [l] in foundLandmarks:
                        # verbosePrint("R2", l)
                        landmarks.remove(l)
                verbosePrint(landmarks)
                score = sum([ordering_score(self.l.parse_goal(lm), foundLandmarks)
                             for lm in landmarks]) + 1
                mem_dict[frozenset(landmark)] = score
            verbosePrint("RETURN")
            return score

        def ordering_score2(landmark, combinedLandmarks, foundLandmarks=[]):
            ''' The more sub-landmarks a landmark covers then the earlier it will be executed '''
            score = mem_dict.get(frozenset(landmark))

            if landmark[0] in foundLandmarks:
                verbosePrint("ALREADY FOUND")
                return 0

            if not score:
                mem_dict[frozenset(landmark)] = 1

                ''' Calculate all sub landmarks for this landmark'''
                initialTask = self.l.initialTask
                initialTask.goals = landmark
                landmarks = get_landmarks(initialTask)
                filteredLandmarks = list(filter(lambda l: [l] in combinedLandmarks and [
                    l] != landmark, landmarks))
                verbosePrint("GENERATED LANDMARKS:", landmarks)

                ''' Check how many landmarks are contained within the combinedLandmarks list'''
                for l in filteredLandmarks:
                    verbosePrint("DIGGING INTO ", l)

                    subs = ordering_score2(
                        [l], combinedLandmarks, foundLandmarks)
                    foundLandmarks.append(l)
                    verbosePrint(l, "had", subs)
                    mem_dict[frozenset(landmark)] += subs
                verbosePrint("Calculated", mem_dict.get(
                    frozenset(landmark)), landmark)
                return mem_dict.get(frozenset(landmark))
            else:
                verbosePrint("Pre calculated", score, landmark)
                return score

        def intersection(lst1, lst2):
            lst3 = [value for value in lst1 if value in lst2]
            return lst3

        landmarkIntersection = [intersection(i,
                                             self.l.getRealLandmark()) for i in self.l.landmarks]
        # Intersection with self to empty set
        landmarkIntersection[self.l.realGoalIndex] = {}
        verbosePrint(
            "# Intersection of goals with the real goal",
            *[f"{i}: {a} " if i != self.l.realGoalIndex else "" for i, a in enumerate(landmarkIntersection)])

        maximumIntersectionIndex = landmarkIntersection.index(max(
            landmarkIntersection, key=len))  # Result has an index of the maximum intersection
        closestLandmarks = self.l.getLandmark(maximumIntersectionIndex)
        realGoalLandmarks = self.l.getRealLandmark()
        combinedLandmarks = closestLandmarks
        for landmark in realGoalLandmarks:
            if landmark not in combinedLandmarks:
                combinedLandmarks.append(landmark)
                
        sortedLandmarks = sorted(
            combinedLandmarks, key=lambda landmark: ordering_score2(landmark, combinedLandmarks))
        verbosePrint(mem_dict)
        # input()
        sortedLandmarks.append(self.l.getRealGoal(True))
        return(sortedLandmarks)


class MostCommonLandmarks(ApproachTemplate):
    NAME = "Most Common Landmarks"
    DESC = "Achieves the most common landmarks of the real goal first"

    def __init__(self, extractedLandmarks: ExtractLandmarks):
        super().__init__(extractedLandmarks)

    def generate(self):
        landmarkScoring = []
        for landmark in self.l.getRealLandmark():

            task = self.l.initialTask
            task.goals = landmark
            heuristic = LandmarkHeuristic(task)

            path = astar_search(task, heuristic)

            numberPresent = 0
            for candidateLandmarks in self.l.landmarks:
                if landmark in candidateLandmarks:
                    numberPresent += 1
            l, = landmark
            index = -1
            for ordering in self.l.landmark_ordering:
                if ordering[0] == l:
                    index = ordering[1]
            landmarkScoring.append((landmark, numberPresent, len(path), index))

        landmarkScoring = sorted(
            landmarkScoring, key=lambda x: x[3])
        landmarkScoring = sorted(
            landmarkScoring, key=lambda x: x[2])
        landmarkScoring = sorted(
            landmarkScoring, key=lambda x: x[1], reverse=True)

        ordered_l = list(map(lambda x: x[0], landmarkScoring))
        ordered_l.append(self.l.getRealGoal(True))

        return ordered_l


class ApproachTester():
    ############################################
    ### FUNCTIONS INTERACTING WITH LANDMARKS ###
    ############################################
    def __init__(self, *args: ApproachTemplate, extracted: ExtractLandmarks):
        self.approaches = [*args]
        self.l = extracted

    def testApproaches(self):
        def pathToGoal(acc, goal):
            ''' Given a task and a landmark, calculate the number of steps to achieve this landmark
            and calculate the end state after traversing the path. Deception keeps track of whether FTP and LDP have been reached in form of (BOOLEAN,BOOLEAN)
            '''
            task, steps, deception_array, ops = acc
            verbosePrint(f"###### Finding path to {goal} #####")

            task.goals = goal
            heuristic = LandmarkHeuristic(task)
            actual = astar_search_custom(
                task, heuristic, return_state=True)  # Patrick's edited code
            path = astar_search(task, heuristic)  # Generate a path

            # Applying these ops to the state

            for op in path:
                steps += 1
                verbosePrint(f"Current State: {task.initial_state}")
                verbosePrint(f"Applying step {steps}: {op}")
                # TODO Check deceptivity here rather than at landmarks
                task.initial_state = op.apply(task.initial_state)
                
                if argparser.parse_args().deceptivestats:
                    verbosePrint(f"Calculating deceptive stats")
                    deception_array.append(self.deceptive_stats(task))
            if path != []:
                ops.append(path)
            assert task.initial_state == actual  # Making sure the final state is correct
            return task, steps, deception_array, ops

        for approach in self.approaches:
            verbosePrint(f"##### Approach: {approach.NAME} #####")
            
            outputRow = csvOutput.addNewRow()
            outputRow.approachName = approach.NAME

            parser = Parser(self.l.domainFile, self.l.tempLoc("task0.pddl"))
            dom = parser.parse_domain()
            problem = parser.parse_problem(dom)

            initialTask = _ground(problem)

            outputRow.initialState = initialTask.initial_state
            generationStart = time.time()
            orderedPath = approach(self.l).generate()
            task, steps, deception_array, ops = functools.reduce(
                pathToGoal, orderedPath, (initialTask, 0, [], []))
            generationEnd = time.time()


            outputRow.goalState = task.goals
            outputRow.pathLength = steps
            outputRow.path = ops
            outputRow.time = generationEnd - generationStart

            if not argparser.parse_args().deceptivestats:
                continue
            outputRow.deceptiveStats = deception_array
            _, _, optimal_deception_array, _ = functools.reduce(
                pathToGoal, [orderedPath[-1]], (_ground(problem), 0, [], []))

            calc = self.l.getRealGoal(True)

            rmp = self.generate_rmp()
            deception_before_rmp = deception_array[: len(
                deception_array) - math.ceil(rmp)]
            deceptive_steps = len(
                list(filter(lambda x: not x[0], deception_before_rmp)))
            score = (len(deception_array) - self.l.optimal_plans[self.l.realGoalIndex]) / \
                ((deceptive_steps / len(deception_before_rmp)) * 100)

            deceptivePercent = (len(deception_array) - rmp) / \
                (self.l.optimal_plans[self.l.realGoalIndex] - rmp)

            truthfulSteps = len(deception_array) - deceptive_steps
            deceptiveness = 1 - (truthfulSteps / len(deception_array))

            optimal_deception_before_rmp = optimal_deception_array[: len(
                optimal_deception_array) - math.ceil(rmp)]
            optimal_deceptive_steps = len(
                list(filter(lambda x: not x[0], optimal_deception_before_rmp)))

            optimalTruthfulSteps = len(
                optimal_deception_array) - optimal_deceptive_steps
            optimalDeceptiveness = 1 - \
                (optimalTruthfulSteps / len(optimal_deception_array))

            deceptiveness = (1 -
                             (truthfulSteps / len(deception_array))) / optimalDeceptiveness

            combined = deceptivePercent / deceptiveness
            scores = [deceptivePercent, deceptiveness, combined]

            outputRow.extraCost = deceptivePercent
            outputRow.extraDeceptiveness = deceptiveness

            # check that the goal is indeed reached
            # assert calc.issubset(task.initial_state)
            verbosePrint(
                f"FINAL RESULT: {steps} steps taken to reach final goal.")
            deceptive_stats = self.calc_deceptive_stats(deception_array)
            # self.plot(deception_array, approach, scores)
            verbosePrint(f"Density of deception: {deceptive_stats[0]}")
            verbosePrint(f"Extent of deception: {deceptive_stats[1]}")

    def plot(self, deception_array, approach, scores):
        dir = "temp/"
        plt.figure(figsize=(10, 8))
        plt.title(f"Approach Type: {approach.NAME} \n Scores: {scores}")
        pathlength = self.l.optimal_plans[self.l.realGoalIndex]
        df = pd.DataFrame(deception_array, columns=[
            'deceptive', 'deceptiveness'])
        for i in range(len(df)):
            color = 'r' if df['deceptive'][i] else 'b'
            plt.scatter(i, -1 * (df['deceptiveness']
                        [i] - pathlength), color=color)
        #
        plt.xlabel("Steps")
        plt.ylabel("Optimal Steps to Goal",)
        plt.legend(handles=[mpatches.Patch(
            color='r', label='Non-Deceptive'), mpatches.Patch(color='b', label='Deceptive')])
        plt.savefig(os.path.join(os.path.dirname(__file__),
                    OUTPUT_DIR) + f"/{approach.NAME}.png")
    ########################
    ### USEFUL FUNCTIONS ###
    ########################

    def optc(self, goal, state_task):  # TODO Refactor to output path completion as well as cost_dif
        '''
        Calculates the optimal cost from current state to goal. Can be used to calculate cost diff and probability distributions.

        @param goal:  Integer specifying goal from self.goals list
        @param state_task: Task instance for current state
        @return: integer representation of length of path from current state to the given goal.
        '''
        original_goal = state_task.goals
        state_task.goals = self.l.getGoal(goal, True)
        heuristic = LmCutHeuristic(state_task)
        state_plan = astar_search(state_task, heuristic)
        state_task.goals = original_goal
        return len(state_plan)

    # TODO Refactor to output path completion as well as cost_dif
    def optc_for_task(self, state_task):
        '''
        Calculates the optimal cost from current state to goal. Can be used to calculate cost diff and probability distributions.

        @param goal:  Integer specifying goal from self.goals list
        @param state_task: Task instance for current state
        @return: integer representation of length of path from current state to the given goal.
        '''
        heuristic = LmCutHeuristic(state_task)
        state_plan = astar_search(state_task, heuristic)
        verbosePrint(state_task.initial_state, '  ->  ',
                     state_task.goals, '\n', state_plan, '\n')

        if state_plan is None:
            return math.inf
        return len(state_plan)

    def deceptive_stats(self, state_task):
        '''
        Calculates statistics related to deception for a certain state such as truthfulness and plan completion.
        @param state_task: Task instance for current state
        @return:
        '''
        opt_state_to_goal = self.optc(self.l.realGoalIndex, state_task)
        true_cost_diff = opt_state_to_goal - \
            self.l.optimal_plans[self.l.realGoalIndex]
        truthful = False
        for i in range(len(self.l.goals)):
            if i == self.l.realGoalIndex:
                pass
            else:
                if true_cost_diff < (self.optc(i, state_task) - self.l.optimal_plans[i]):
                    truthful = True
        plan_completion = opt_state_to_goal
        return truthful, plan_completion

    def calc_deceptive_stats(self, deception_array):
        truths = 0
        LDP_path_comp = 0
        for state in deception_array:
            if state[0]:
                truths += 1
            else:
                LDP_path_comp = state[1]
        return 1 / truths, LDP_path_comp

    def generate_rmp(self):
        rmp_values = []

        for goal in self.l.goals:

            if goal == self.l.getRealGoal():
                continue

            verbosePrint(f"Calculating RMP...")
            verbosePrint(goal)
            candidate_goal = self.l.parse_goal(goal)

            start_to_real = _ground(
                _parse(self.l.domainFile, self.l.tempLoc("task0.pddl")))
            heuristic = LmCutHeuristic(start_to_real)
            start_to_real_path = astar_search(start_to_real, heuristic)
            start_to_real_cost = len(start_to_real_path)

            verbosePrint(f"start_to_real length: {start_to_real_cost}")

            start_to_candidate = _ground(
                _parse(self.l.domainFile, self.l.tempLoc("task0.pddl")))
            start_to_candidate.goals = candidate_goal
            heuristic = LmCutHeuristic(start_to_candidate)
            start_to_candidate_path = astar_search(
                start_to_candidate, heuristic)
            start_to_candidate_cost = len(
                start_to_candidate_path)

            verbosePrint(
                f"start_to_candidate_cost length: {start_to_candidate_cost}")

            real_to_candidate = _ground(
                _parse(self.l.domainFile, self.l.tempLoc("task0.pddl")))

            for op in start_to_real_path:
                real_to_candidate.initial_state = op.apply(
                    real_to_candidate.initial_state)
            real_to_candidate.goals = candidate_goal

            heuristic = LmCutHeuristic(real_to_candidate)
            real_to_candidate_cost = len(
                astar_search(real_to_candidate, heuristic))

            verbosePrint(
                f"real_to_candidate_cost length: {real_to_candidate_cost}")

            rmp_values.append((real_to_candidate_cost + start_to_real_cost -
                              start_to_candidate_cost) / 2)

        verbosePrint(f"rmp value: {min(rmp_values)}, rmp array: {rmp_values}")

        return min(rmp_values)


if __name__ == "__main__":
    DIR = os.path.dirname(__file__)
    # Defining constants
    EXPERIMENTS_DIR = os.path.join(DIR, 'experiment-data/experiment-input')
    TEMP_DIR = os.path.join(DIR, 'temp')

    argparser = argparse.ArgumentParser(
        description='Create deceptive plans for the provided planning domains in experiment-data/experiment-input')
    argparser.add_argument('--verbose', dest='verbose', action='store_const',
                           const=True, default=False,
                           help='include detailed info about script progress')
    argparser.add_argument('--deceptivestats', dest='deceptivestats', action='store_const',
                           const=True, default=False,
                           help='include more deceptive stats in the output (this will increase runtime substantially)')

    # Location of output folder

    # Iterate through each problem set
    for _, dirs, _ in os.walk(EXPERIMENTS_DIR):
        for dname in dirs:
            domaindir = f"{EXPERIMENTS_DIR}/{dname}/domain.pddl"
            hypsdir = f"{EXPERIMENTS_DIR}/{dname}/hyps.dat"
            realhypdir = f"{EXPERIMENTS_DIR}/{dname}/real_hyp.dat"
            templatedir = f"{EXPERIMENTS_DIR}/{dname}/template.pddl"
            OUTPUT_DIR = os.path.join(
                DIR, f"experiment-data/experiment-output/{dname}")
            if os.path.exists(OUTPUT_DIR):
                shutil.rmtree(OUTPUT_DIR)

            os.mkdir(OUTPUT_DIR)

            csvOutput = CSVApproachOutput()
            csvDomainOutput = CSVDomainOutput()

            # sys.stdout = open(os.path.join(
            #     OUTPUT_DIR, f"{dname}result.txt"), 'w+')
            extractionTimerStart = time.time()
            extracted = ExtractLandmarks(
                domaindir, hypsdir, realhypdir, templatedir, debug=True)
            extractionTimerEnd = time.time()

            for x in range (0, len(extracted.goals)):
                domainOutput = csvDomainOutput.addNewRow()
                domainOutput.domainName = dname
                domainOutput.goalState = extracted.getGoal(x)
                domainOutput.landmarks = extracted.getLandmark(x)
                domainOutput.initialState = extracted.initialTask.initial_state
                domainOutput.isRealGoal = str(extracted.getGoal(x)) == str(extracted.getRealGoal())
                domainOutput.extractionTime = extractionTimerEnd - extractionTimerStart

            a1 = ApproachTester(BaselineApproach, GoalToRealGoalApproach, OldScoringApproach,
                                NewScoringApproach, MostCommonLandmarks, extracted=extracted)
            a1.testApproaches()
            csvOutput.writeToCSV(f"{dname}-approaches")
            csvDomainOutput.writeToCSV(dname)
