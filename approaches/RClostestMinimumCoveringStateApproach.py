from approaches.ApproachTemplate import ApproachTemplate
from approaches.CentroidsApproach import CentroidsApproach
from pyperplanmaster.src.pyperplan.search.a_star import astar_search
from pyperplanmaster.src.pyperplan.heuristics.landmarks import *
from os.path import exists


import re

class RClosestMinimumCoveringStateApproach(CentroidsApproach):
    NAME = "R-Closest Minimum Covering State Approach"
    DESC = "Achieves the centroid between the real goal and closest goal, then the real goal"

    def __init__(self, extractedLandmarks, realTask, hashableRealGoal, dname):
        from generatePlans import EXPERIMENTS_DIR
        super().__init__(extractedLandmarks, realTask, hashableRealGoal, dname)
        self.centroidsFile = "r-minimum-covering_heuristic_greedy-real_goal-closest_goal.txt"