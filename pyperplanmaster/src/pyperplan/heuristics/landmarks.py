#
# This file is part of pyperplan.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

"""
Landmarks Heuristic
"""

from collections import defaultdict
import copy

from .heuristic_base import Heuristic


def _get_relaxed_task(task):
    """
    Removes the delete effects of every operator in task
    """
    relaxed_task = copy.deepcopy(task)
    for op in relaxed_task.operators:
        op.del_effects = []
    return relaxed_task


def get_landmarks(task, ordering=False):
    """Returns a set of landmarks.

    In this implementation a fact is a landmark if the goal facts cannot be
    reached without it.
    """
    task = _get_relaxed_task(task)
    landmarks = task.goals
    landmark_order = [(item, index) for index, item in enumerate(landmarks)]
    possible_landmarks = list(
        filter(lambda x: x not in task.goals, task.facts))

    for fact in possible_landmarks:
        current_state = task.initial_state
        goal_reached = frozenset(current_state) >= frozenset(task.goals)

        while not goal_reached:
            previous_state = current_state

            for op in task.operators:
                if op.applicable(current_state) and fact not in op.add_effects:
                    current_state = op.apply(current_state)
                    if frozenset(current_state) >= frozenset(task.goals):
                        break
            if previous_state == current_state and not frozenset(current_state) >= frozenset(task.goals):
                landmarks.append(fact)
                landmark_order.append((fact, len(landmarks)))
                break

            goal_reached = frozenset(current_state) >= frozenset(task.goals)
    # print(landmarks)
    return (landmarks, landmark_order) if ordering else landmarks


def compute_landmark_costs(task, landmarks):
    """
    Compute uniform cost partitioning for actions depending on the landmarks
    they achieve.
    """
    op_to_lm = defaultdict(set)
    for operator in task.operators:
        for landmark in landmarks:
            if landmark in operator.add_effects:
                op_to_lm[operator].add(landmark)
    min_cost = defaultdict(lambda: float("inf"))
    for operator, landmarks in op_to_lm.items():
        landmarks_achieving = len(landmarks)
        for landmark in landmarks:
            min_cost[landmark] = min(
                min_cost[landmark], 1 / landmarks_achieving)
    return min_cost


class LandmarkHeuristic(Heuristic):
    def __init__(self, task, output=False):
        self.task = task
        self.landmarks = get_landmarks(task)
        assert self.task.goals <= self.landmarks
        self.costs = compute_landmark_costs(task, self.landmarks)

    def __call__(self, node):
        """Returns the heuristic value for "node"."""
        if node.parent is None:
            # At the beginning only the initial facts are achieved
            node.unreached = list(filter(
                lambda x: x not in self.task.initial_state, self.landmarks))
        else:
            # A new node reaches the facts in its add_effects
            node.unreached = list(filter(
                lambda x: x not in node.action.add_effects, node.parent.unreached))
        # We always want to keep the goal facts unreached if they are not true
        # in the current state, even if they have been reached before
        unreached = node.unreached
        extra = list(filter(lambda x: x not in node.state, self.task.goals))
        for elem in extra:
            if elem not in unreached:
                unreached.append(elem)

        h = sum(self.costs[landmark] for landmark in unreached)
        return h
