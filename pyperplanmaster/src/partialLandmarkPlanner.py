from src.pyperplan.planner import (
    HEURISTICS,
    _parse
)
from grounding import ground
from pddl.parser import Parser
import os
from src.pyperplan.search.a_star import astar_search


def landmark_to_landmark(landmark1, landmark2, domain, problem):
    parser = Parser(domain, problem)
    domain = parser.parse_domain()
    problem = parser.parse_problem(domain)
    task = ground(problem)
    # Get state(list of predicates) after planning from init to landmark1
    task.goals = frozenset({landmark1})
    heuristic = HEURISTICS['landmark'](task)
    state_at_landmark1 = astar_search(task, heuristic, return_state=True)
    # Create new task using state as init and landmark2 as sole goal
    between_landmarks = task
    between_landmarks.goals = frozenset({landmark2})
    between_landmarks.initial_state = state_at_landmark1
    heuristic = HEURISTICS['landmark'](between_landmarks)
    return astar_search(between_landmarks, heuristic)


if __name__ == "__main__":
    root = "./toy problems"
    domain_file = os.path.join(root, "domain.pddl")
    problem_file = os.path.join(root, "aToyLogistics.pddl")
    print(landmark_to_landmark("(in pkg3 t)", "(at pkg3 arp2)", domain_file, problem_file))
