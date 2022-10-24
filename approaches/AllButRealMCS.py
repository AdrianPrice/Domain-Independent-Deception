from approaches.ApproachTemplate import ApproachTemplate
from approaches.CentroidsApproach import CentroidsApproach
from pyperplanmaster.src.pyperplan.search.a_star import astar_search
from pyperplanmaster.src.pyperplan.heuristics.landmarks import *
from os.path import exists


import re

class AllButRealMCSApproach(CentroidsApproach):
    NAME = "All but Real Minimum Coverinst State Approach"
    DESC = "Achieves the centroid between the candidate goals excluding the real goal, then the real goal"

    def __init__(self, extractedLandmarks, realTask, hashableRealGoal, dname):
        from generatePlans import EXPERIMENTS_DIR
        super().__init__(extractedLandmarks, realTask, hashableRealGoal, dname)
        self.centroidsFile = "minimum-covering_heuristic_greedy-no_real_goal.txt"