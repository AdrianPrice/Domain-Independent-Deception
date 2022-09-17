from approaches.ApproachTemplate import ApproachTemplate

class BaselineApproach(ApproachTemplate):
    NAME = "Baseline Approach"
    DESCRIPTION = """
    Calculates the optimal path from the initial state to the real goal.
    """

    def __init__(self, extractedLandmarks, realTask, hashableRealGoal, dname):
        super().__init__(extractedLandmarks, realTask, hashableRealGoal, dname)

    def generate(self):
        ordered_l = []
        ordered_l.append(self.realTask.goals)
        return ordered_l