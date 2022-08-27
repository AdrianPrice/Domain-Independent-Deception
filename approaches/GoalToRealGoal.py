from approaches.ApproachTemplate import ApproachTemplate
import re

class GoalToRealGoalApproach(ApproachTemplate):
    NAME = "Goal to Real Goal Approach"
    DESCRIPTION = """
    Calculates a path from the initial state to a candidate goal which has the
    most landmarks in common with the real goal.
    """

    def __init__(self, extractedLandmarks, realTask, hashableRealGoal):
        super().__init__(extractedLandmarks, realTask, hashableRealGoal)

    def generate(self):
        '''
        Method for picking landmarks:
            - The goal with the most landmarks in common with the real goal is the most in common.
        '''
        def intersection(lst1, lst2):
            lst3 = [value for value in lst1 if value in lst2]
            return lst3
            
        realGoalLandmarks = self.l[self.hashableRealGoal]
        landmarkIntersection = {}
        for key in self.l:
            if key != self.hashableRealGoal:
                landmarkIntersection[key] = intersection(realGoalLandmarks, self.l[key])
        
        maxGoal = (None, -1)
        for sharedLandmarks in landmarkIntersection.items():
            if len(sharedLandmarks[1]) > maxGoal[1]:
                maxGoal = (sharedLandmarks[0], len(sharedLandmarks[1]))

        ordered_l = []
        ordered_l.append(re.findall('\([A-Za-z0-9  \-\_]*\)', maxGoal[0]))
        ordered_l.append(self.realTask.goals)
        
        return ordered_l