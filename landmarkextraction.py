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


def verbosePrint(data):
    if argparser.parse_args().verbose:
        print(data)


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
        print(f"##### Getting landmarks #####")
        self.domainFile: str = os.path.abspath(domaindir)
        with open(hypsdir) as goalsfile:
            self.goals: list[str] = goalsfile.read().splitlines()
        with open(realhypdir) as realhypfile:
            self.realGoalIndex: int = self.goals.index(realhypfile.readline())
        with open(templatedir) as templatefile:
            self.taskTemplate: str = templatefile.read()

        # DEBUG
        print('# List of Goals parsed: #\n',
              *[f"{i} : {a}\n" for i, a in enumerate(self.goals)])
        print('# Real Goal parsed: #\n',
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
            # print(task)
            if self.initialTask == None:
                self.initialTask = task
            landmarks, self.landmark_ordering = get_landmarks(task, True)
            landmarks_set = list(map(self.parse_goal, landmarks))
            self.landmarks.append(landmarks_set)

        print('# List of Landmarks calculated:\n',
              * [f"{i} : {self.goals[i]} : {a}\n" for i, a in enumerate(self.landmarks)])

    def tempLoc(self, name):
        ''' Returns an absolute directory to the temp location.
        '''
        return os.path.join(self.TEMP_DIR, name)

    def parse_goal(self, goal):
        print("parsing ", goal)
        parsedgoals = re.findall('\([A-Za-z0-9 ]*\)', goal)
        print("parsed", parsedgoals)
        return parsedgoals

    def generate_optimal(self):
        optimal_paths = []
        goal_task = _ground(
            _parse(self.domainFile, self.tempLoc("task0.pddl")))
        for goal in self.goals:
            print(f"Calculating OPTIMAL...")
            print(goal)
            goal_task.goals = self.parse_goal(goal)
            heuristic = LmCutHeuristic(goal_task)
            goal_plan = astar_search(goal_task, heuristic)
            optimal_paths.append(len(goal_plan))
            print(f"Calculated length: {len(goal_plan)}")
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
        # print(
        # "# Intersection of goals with the real goal",
        # *[f"{i}: {a} " if i != self.l.realGoalIndex else "" for i, a in enumerate(landmarkIntersection)])
        # print(landmarkIntersection)
        landmarkSetIndex = landmarkIntersection.index(
            max(landmarkIntersection, key=len))  # Result has a list of landmarks
        print(
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
            print(f"LANDMARKS:{landmark} : {landmarks}")
            print(f"Landmark: {landmark}, Score: {len(landmarks)}")
            return len(landmarks)

        # PICKING LANDMARKS
        def intersection(lst1, lst2):
            lst3 = [value for value in lst1 if value in lst2]
            return lst3

        landmarkIntersection = [intersection(i,
                                             self.l.getRealLandmark()) for i in self.l.landmarks]
        # Intersection with self to empty set
        landmarkIntersection[self.l.realGoalIndex] = {}
        print(
            "# Intersection of goals with the real goal",
            *[f"{i}: {a} " if i != self.l.realGoalIndex else "" for i, a in enumerate(landmarkIntersection)])

        # Result has a list of landmarks
        landmarkSet = max(landmarkIntersection, key=len)
        print(
            "# The intersection with the largest number of landmarks",
            *[f"{i}: {a} " for i, a in enumerate(landmarkSet)])

        # LANDMARK ORDERING
        print(f"# Sorting based on score")
        print(landmarkSet)
        ordered_l = sorted(
            landmarkSet, key=lambda landmark: ordering_score(landmark))
        print(f"Sorted based on score: {ordered_l}")
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
            print("F", foundLandmarks)
            ''' Order landmarks based on similiarity to the initial task '''
            input()
            core = mem_dict.get(frozenset(landmark))
            print(landmark, score)
            if not score:
                # calculate score if it isnt already in the dictionary
                initialTask = self.l.initialTask
                initialTask.goals = landmark
                # get the landmarks of this landmark
                landmarks = get_landmarks(initialTask)
                print(landmarks, set(landmark).issubset(set(landmarks)))
                if set(landmark).issubset(set(landmarks)):
                    for l in landmark:
                        print("removed ", l)
                        landmarks.remove(l)
                foundLandmarks.append(landmark)
                print("L", landmarks)
                for l in landmarks:
                    # print("HI", [l], landmarks)
                    if [l] in foundLandmarks:
                        # print("R2", l)
                        landmarks.remove(l)
                print(landmarks)
                score = sum([ordering_score(self.l.parse_goal(lm), foundLandmarks)
                             for lm in landmarks]) + 1
                mem_dict[frozenset(landmark)] = score
            print("RETURN")
            return score

        def ordering_score2(landmark, combinedLandmarks, foundLandmarks=[]):

            # def list_subgoals(landmark, combinedLandmarks, foundLandmarks=[]):
            #     print(foundLandmarks)
            #     print(landmark)
            #     print(landmark[0] in foundLandmarks)
            #
            #     if landmark[0] in foundLandmarks:
            #         return []
            #     initialTask = self.l.initialTask
            #     initialTask.goals = landmark
            #     landmarks = get_landmarks(initialTask)
            #     print(landmarks)
            #     print("~~~~~~~~~~~~")
            #     # input()
            #     filteredLandmarks = list(filter(lambda l: [l] in combinedLandmarks and [
            #         l] != landmark, landmarks))
            #
            #     for l in filteredLandmarks:
            #         # print(l, filteredLandmarks)
            #         removed = list(
            #             filter(lambda x: x != l, filteredLandmarks))
            #         subs = list_subgoals(
            #             [l], combinedLandmarks, foundLandmarks + removed)
            #         filteredLandmarks = filteredLandmarks + subs
            #         foundLandmarks = foundLandmarks + subs
            #     return filteredLandmarks
            #
            # subs = list_subgoals(landmark, combinedLandmarks)
            # print(subs)
            # return len(subs)

            # input()
            # print("STARTING FROM", landmark)
            # print("~")
            # print(combinedLandmarks)
            # print("~")
            # print(foundLandmarks)
            ''' The more sub-landmarks a landmark covers then the earlier it will be executed '''
            score = mem_dict.get(frozenset(landmark))

            if landmark[0] in foundLandmarks:
                print("ALREADY FOUND")
                return 0

            if not score:
                mem_dict[frozenset(landmark)] = 1

                ''' Calculate all sub landmarks for this landmark'''
                initialTask = self.l.initialTask
                initialTask.goals = landmark
                landmarks = get_landmarks(initialTask)
                filteredLandmarks = list(filter(lambda l: [l] in combinedLandmarks and [
                    l] != landmark, landmarks))
                print("GENERATED LANDMARKS:", landmarks)

                ''' Check how many landmarks are contained within the combinedLandmarks list'''
                for l in filteredLandmarks:
                    print("DIGGING INTO ", l)

                    subs = ordering_score2(
                        [l], combinedLandmarks, foundLandmarks)
                    foundLandmarks.append(l)
                    print(l, "had", subs)
                    mem_dict[frozenset(landmark)] += subs
                print("Calculated", mem_dict.get(
                    frozenset(landmark)), landmark)
                return mem_dict.get(frozenset(landmark))
            else:
                print("Pre calculated", score, landmark)
                return score

        def intersection(lst1, lst2):
            lst3 = [value for value in lst1 if value in lst2]
            return lst3

        landmarkIntersection = [intersection(i,
                                             self.l.getRealLandmark()) for i in self.l.landmarks]
        # Intersection with self to empty set
        landmarkIntersection[self.l.realGoalIndex] = {}
        print(
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
        print(mem_dict)
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
        def writeToOutputFile(self, text):
            f = open(os.path.join(os.path.dirname(__file__),
                                  OUTPUT_DIR) + f"/{approach.NAME}.txt", "a")
            f.write(f"{str(text)}\n")
            f.close()

        def pathToGoal(acc, goal):
            ''' Given a task and a landmark, calculate the number of steps to achieve this landmark
            and calculate the end state after traversing the path. Deception keeps track of whether FTP and LDP have been reached in form of (BOOLEAN,BOOLEAN)
            '''
            task, steps, deception_array = acc
            print(f"###### Finding path to {goal} #####")

            task.goals = goal
            heuristic = LandmarkHeuristic(task)
            actual = astar_search_custom(
                task, heuristic, return_state=True)  # Patrick's edited code
            path = astar_search(task, heuristic)  # Generate a path
            writeToOutputFile(approach, path)

            # Applying these ops to the state

            for op in path:
                steps += 1
                print(f"Current State: {task.initial_state}")
                print(f"Applying step {steps}: {op}")
                # TODO Check deceptivity here rather than at landmarks
                task.initial_state = op.apply(task.initial_state)

                deception_array.append(self.deceptive_stats(task))
            assert task.initial_state == actual  # Making sure the final state is correct
            return task, steps, deception_array

        for approach in self.approaches:
            print(f"##### Approach: {approach.NAME} #####")
            parser = Parser(self.l.domainFile, self.l.tempLoc("task0.pddl"))
            dom = parser.parse_domain()
            problem = parser.parse_problem(dom)
            initialTask = _ground(problem)
            orderedPath = approach(self.l).generate()
            task, steps, deception_array = functools.reduce(
                pathToGoal, orderedPath, (initialTask, 0, []))

            if not argparser.parse_args().verbose:
                continue

            _, _, optimal_deception_array = functools.reduce(
                pathToGoal, [orderedPath[-1]], (_ground(problem), 0, []))

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

            # check that the goal is indeed reached
            # assert calc.issubset(task.initial_state)
            print(f"FINAL RESULT: {steps} steps taken to reach final goal.")
            deceptive_stats = self.calc_deceptive_stats(deception_array)
            self.plot(deception_array, approach, scores)
            print(f"Density of deception: {deceptive_stats[0]}")
            print(f"Extent of deception: {deceptive_stats[1]}")

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
        print(state_task.initial_state, '  ->  ',
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
        plan_completion = self.l.optimal_plans[self.l.realGoalIndex] - \
            opt_state_to_goal
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

            print(f"Calculating RMP...")
            print(goal)
            candidate_goal = self.l.parse_goal(goal)

            start_to_real = _ground(
                _parse(self.l.domainFile, self.l.tempLoc("task0.pddl")))
            heuristic = LmCutHeuristic(start_to_real)
            start_to_real_path = astar_search(start_to_real, heuristic)
            start_to_real_cost = len(start_to_real_path)

            print(f"start_to_real length: {start_to_real_cost}")

            start_to_candidate = _ground(
                _parse(self.l.domainFile, self.l.tempLoc("task0.pddl")))
            start_to_candidate.goals = candidate_goal
            heuristic = LmCutHeuristic(start_to_candidate)
            start_to_candidate_path = astar_search(
                start_to_candidate, heuristic)
            start_to_candidate_cost = len(
                start_to_candidate_path)

            print(f"start_to_candidate_cost length: {start_to_candidate_cost}")

            real_to_candidate = _ground(
                _parse(self.l.domainFile, self.l.tempLoc("task0.pddl")))

            for op in start_to_real_path:
                real_to_candidate.initial_state = op.apply(
                    real_to_candidate.initial_state)
            real_to_candidate.goals = candidate_goal

            heuristic = LmCutHeuristic(real_to_candidate)
            real_to_candidate_cost = len(
                astar_search(real_to_candidate, heuristic))

            print(f"real_to_candidate_cost length: {real_to_candidate_cost}")

            rmp_values.append((real_to_candidate_cost + start_to_real_cost -
                              start_to_candidate_cost) / 2)

        print(f"rmp value: {min(rmp_values)}, rmp array: {rmp_values}")

        return min(rmp_values)


if __name__ == "__main__":
    DIR = os.path.dirname(__file__)
    # Defining constants
    EXPERIMENTS_DIR = os.path.join(DIR, 'experiment-data/experiment-input')
    TEMP_DIR = os.path.join(DIR, 'temp')

    argparser = argparse.ArgumentParser(
        description='Create deceptive plans for the provided planning domains in experiment-data/experiment-input')
    argparser.add_argument('--verbosedata', dest='verbose', action='store_const',
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

            # sys.stdout = open(os.path.join(
            #     OUTPUT_DIR, f"{dname}result.txt"), 'w+')
            extracted = ExtractLandmarks(
                domaindir, hypsdir, realhypdir, templatedir, debug=True)

            a1 = ApproachTester(BaselineApproach, GoalToRealGoalApproach, OldScoringApproach,
                                NewScoringApproach, MostCommonLandmarks, extracted=extracted)
            a1.testApproaches()
