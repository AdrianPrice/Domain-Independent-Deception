from approaches.ApproachTemplate import ApproachTemplate
from pyperplanmaster.src.pyperplan.search.a_star import astar_search
from pyperplanmaster.src.pyperplan.heuristics.landmarks import *
from pyperplanmaster.src.pyperplan.search.breadth_first_search import breadth_first_search

import re

class MostCommonLandmarks(ApproachTemplate):
    NAME = "Most Common Landmarks"
    DESC = "Achieves the most common landmarks of the real goal first"

    def __init__(self, extractedLandmarks, realTask, hashableRealGoal, dname):
        super().__init__(extractedLandmarks, realTask, hashableRealGoal, dname)

    def generate(self):
        landmarkScoring = []
        for landmark in self.l[self.hashableRealGoal]:

            task = self.realTask
            
            task.goals = [landmark]

            path = breadth_first_search(task)

            numberPresent = 0
            for candidateLandmarks in self.l.items():
                if landmark in candidateLandmarks[1]:
                    numberPresent += 1
                    
            landmarkScoring.append((landmark, numberPresent, len(path)))

        landmarkScoring = sorted(
            landmarkScoring, key=lambda x: x[2])
        landmarkScoring = sorted(
            landmarkScoring, key=lambda x: x[1], reverse=True)

        ordered_l = list(map(lambda x: re.findall('\([A-Za-z0-9  \-\_]*\)', x[0]), landmarkScoring))
        ordered_l.append(re.findall('\([A-Za-z0-9  \-\_]*\)', self.hashableRealGoal))
        
        return ordered_l