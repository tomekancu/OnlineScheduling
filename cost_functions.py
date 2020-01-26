from typing import Callable
from enum import Enum

from models import Task


# wklesla
def concave_function(task: Task, n: int) -> float:
    return task.base_length / n


# liniowa
def linear_function(task: Task, n: int) -> float:
    max_val = task.base_length / task.min_resources
    min_val = task.base_length / task.max_resources
    len_by_proc = (max_val - min_val) / (task.max_resources - task.min_resources)
    how_shorter = (n - task.min_resources) * len_by_proc
    return max_val - how_shorter


# wypukla
def convex_function(task: Task, n: int) -> float:
    b = task.base_length
    max_n = task.max_resources
    min_n = task.min_resources
    return b / (n - (min_n + max_n)) + b / max_n + b / min_n


class LengthFunctionType(Enum):
    CONCAVE = ("CONCAVE", concave_function)
    LINEAR = ("LINEAR", linear_function)
    CONVEX = ("CONVEX", convex_function)

    def __str__(self):
        return self.value[0]

    def __hash__(self):
        return hash(self.value[0])

    def __eq__(self, other):
        return self.value[0] == other.value[0]

    def __lt__(self, other):
        return self.value[0] < other.value[0]

    def __gt__(self, other):
        return self.value[0] > other.value[0]

    def get_function(self) -> Callable[[Task, int], float]:
        return self.value[1]
