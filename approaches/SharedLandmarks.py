from approaches.ApproachTemplate import ApproachTemplate
from pyperplanmaster.src.pyperplan.search.a_star import astar_search
from pyperplanmaster.src.pyperplan.heuristics.landmarks import *
import re

class SharedLandmarksApproach(ApproachTemplate):
    NAME = "Shared Landmark Approach"
    DESCRIPTION = """
        Travels to each landmark which is ordered by the number of "sub landmarks" it covers
        """

    def __init__(self, extractedLandmarks, realTask, hashableRealGoal):
        super().__init__(extractedLandmarks, realTask, hashableRealGoal)

    def generate(self):
        '''
        Method for picking landmarks:
            - The goal with the most landmarks in common with the real goal is the most in common.

        Method for ordering landmarks:
            - This goal's landmarks are ordered based on similiarity to the initial state.
        '''
        def ordering_score(landmark):
            ''' Order landmarks based on distance to initial task '''
            task = self.realTask
            task.goals = [landmark]
            heuristic = LandmarkHeuristic(task)

            path = astar_search(task, heuristic)
            return len(path)

        # PICKING LANDMARKS
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
                
        # LANDMARK ORDERING
        ordered_l = sorted(
            landmarkIntersection[maxGoal[0]], key=lambda landmark: ordering_score(landmark))
        ordered_l = list(map(lambda x: re.findall('\([A-Za-z0-9  \-]*\)', x), ordered_l))
        ordered_l.append(re.findall('\([A-Za-z0-9  \-]*\)', self.hashableRealGoal))
        
        return ordered_l