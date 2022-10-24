from approaches.ApproachTemplate import ApproachTemplate
from pyperplanmaster.src.pyperplan.search.a_star import astar_search
from pyperplanmaster.src.pyperplan.heuristics.landmarks import *
from os.path import exists
from os import walk


import re

class CentroidsApproach(ApproachTemplate):
    NAME = "Centroid Approach"
    DESC = "Achieves the centroid, then the real goal first"

    def __init__(self, extractedLandmarks, realTask, hashableRealGoal, dname):
        super().__init__(extractedLandmarks, realTask, hashableRealGoal, dname)
        from generatePlans import EXPERIMENTS_DIR
        self.centroidsFile = "centroid_heuristic_greedy.txt"
        self.hypsdir = f"{EXPERIMENTS_DIR}/{self.dname}/hyps.dat"

    def generate(self):
        from generatePlans import EXPERIMENTS_DIR
        filenames = next(walk(f"{EXPERIMENTS_DIR}/{self.dname}"), (None, None, []))[2]  # [] if no file
        centroidFile = list(filter(lambda x: self.centroidsFile in x, filenames))[0]
        centroidsdir = f"{EXPERIMENTS_DIR}/{self.dname}/{centroidFile}"

        if not exists(centroidsdir):
            return [self.realTask.initial_state]

        with open(centroidsdir) as centroidsfile:
            centroid = centroidsfile.read()
            centroidsfile.close()

        with open(self.hypsdir) as hypsfile:
            hyps = hypsfile.read()
            hypsfile.close()

        ordered_l = []
        hypsOps = list(map(lambda x: x.replace("(", ""), re.findall('\([a-z]*\ ', hyps.lower())))

        centroid = ") (".join(list(filter(lambda x : any((("not " not in x) and ("empty-ferry" not in x) and ("handempty " not in x)) for op in hypsOps), centroid.split(") ("))))

        if centroid[-1] != ")":
            centroid += ")"

        ordered_l.append(re.findall('\([A-Za-z0-9  \-\_]*\)', centroid))
        
        ordered_l.append(re.findall('\([A-Za-z0-9  \-\_]*\)', self.hashableRealGoal))

        return ordered_l