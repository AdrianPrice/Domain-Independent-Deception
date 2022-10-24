from approaches.ApproachTemplate import ApproachTemplate
from pyperplanmaster.src.pyperplan.search.breadth_first_search import breadth_first_search
from pyperplanmaster.src.pyperplan.pddl.parser import Parser
from pyperplanmaster.src.pyperplan.planner import _parse, _ground, SEARCHES, HEURISTICS, search_plan
import re
import os

class PetaGoalToRealGoalApproach(ApproachTemplate):
    NAME = "Peta's Goal to Real Goal Approach"
    DESCRIPTION = """
    Calculates a path from the initial state to a candidate goal which has the
    most landmarks in common with the real goal.
    """

    def __init__(self, extractedLandmarks, realTask, hashableRealGoal, dname):
        from generatePlans import EXPERIMENTS_DIR
        super().__init__(extractedLandmarks, realTask, hashableRealGoal, dname)
        templatedir = f"{EXPERIMENTS_DIR}/{self.dname}/{self.dname}.pddl"

        with open(templatedir) as templatefile:
            self.template = templatefile.read()
            templatefile.close()
        self.domaindir = f"{EXPERIMENTS_DIR}/{self.dname}/domain.pddl"
    
    def createTaskFor(self, goals):
        from generatePlans import TEMP_DIR
        parsedGoal = "(and"
        for goal in goals:
            for pred in goal:
                if pred not in parsedGoal:
                    parsedGoal += " " + pred
        parsedGoal += ")"

        problemFile = os.path.join(TEMP_DIR, f"task-temp.pddl")
        task = self.template.replace("<HYPOTHESIS>", parsedGoal)

        with open(problemFile, "w") as create:
                    create.write(task)

        with open(problemFile, "w") as create:
                create.write(task)

        parser = Parser(os.path.abspath(self.domaindir), problemFile)
        dom = parser.parse_domain()
        problem = parser.parse_problem(dom)
        return _ground(problem)

    def generate(self):
        '''
        Method for picking landmarks:
            - The goal with the most landmarks in common with the real goal is the most in common.
        '''
        candidateGoalDistance = []
        for key in self.l:
            if key != self.hashableRealGoal:
                goal = re.findall('\([A-Za-z0-9  \-\_]*\)', key)
                task = self.createTaskFor([goal, self.realTask.goals])
                task.goals = goal

                startToCandidate = breadth_first_search(task)

                if startToCandidate == None:
                    continue

                for op in startToCandidate:
                    task.initial_state = op.apply(task.initial_state)

                task.goals = self.realTask.goals
                candidateToReal = breadth_first_search(task)

                if candidateToReal == None:
                    continue
                candidateGoalDistance.append((goal, len(candidateToReal)))
        
        candidateGoalDistance.sort(key = lambda x: x[1])

        ordered_l = []
        ordered_l.append(candidateGoalDistance[0][0])
        ordered_l.append(self.realTask.goals)
        
        return ordered_l