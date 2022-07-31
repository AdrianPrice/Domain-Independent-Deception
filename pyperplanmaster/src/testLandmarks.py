from src.pyperplan.heuristics.landmarks import LandmarkHeuristic
from src.pyperplan.pddl.parser import Parser
from grounding import ground
import os


def extract_landmarks(directory):
    with open("outputLandmarks.csv", 'w') as f:
        for filename in os.listdir(directory):
            if filename.endswith(".pddl") and filename != "domain.pddl":
                domain_file = os.path.join(directory, "domain.pddl")
                goal_file = os.path.join(directory, filename)
                parser = Parser(domain_file, goal_file)
                domain = parser.parse_domain()
                problem = parser.parse_problem(domain)
                task = ground(problem)
                f.write(filename + ',')
                for landmark in LandmarkHeuristic(task).landmarks:
                    f.write(landmark+',')
                f.write('\n')
            else:
                continue


if __name__ == "__main__":
    goals = "./toy problems"
    extract_landmarks(goals)
