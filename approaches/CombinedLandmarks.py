from approaches.ApproachTemplate import ApproachTemplate
from pyperplanmaster.src.pyperplan.search.breadth_first_search import breadth_first_search
from pyperplanmaster.src.pyperplan.heuristics.landmarks import *
import re
import math

class CombinedLandmarksApproach(ApproachTemplate):
    NAME = "Combined Landmarks Approach"
    DESC = """
    Travels to each landmark which is ordered by the number of "sub landmarks" it covers
    """

    def __init__(self, extractedLandmarks, realTask, hashableRealGoal, dname):
        super().__init__(extractedLandmarks, realTask, hashableRealGoal, dname)

    def generate(self):
        mem_dict = {}
        # PICKING LANDMARKS
        
        def ordering_score(landmark):
            ''' Order landmarks based on distance to initial task '''
            task = self.realTask
            task.goals = [landmark]

            path = breadth_first_search(task)
            
            if path == None:
                return math.inf
            
            return len(path)

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
        closestLandmarks = maxGoal[0]
        
        sharedLandmarks = landmarkIntersection[closestLandmarks]
        closestExclusiveLandmarks = list(filter(lambda x: x not in sharedLandmarks, self.l[closestLandmarks]))
        realExclusiveLandmarks = list(filter(lambda x: x not in sharedLandmarks, self.l[self.hashableRealGoal]))

        sharedLandmarks = sorted(
            sharedLandmarks, key=lambda landmark: ordering_score(landmark))
        closestExclusiveLandmarks = sorted(
            closestExclusiveLandmarks, key=lambda landmark: ordering_score(landmark))
        realExclusiveLandmarks = sorted(
            realExclusiveLandmarks, key=lambda landmark: ordering_score(landmark))
        
        combinedLandmarks = sharedLandmarks + closestExclusiveLandmarks + realExclusiveLandmarks
        combinedLandmarks = list(map(lambda x: re.findall('\([A-Za-z0-9  \-\_]*\)', x), combinedLandmarks))
        combinedLandmarks.append(re.findall('\([A-Za-z0-9  \-\_]*\)', self.hashableRealGoal))
        return(combinedLandmarks)