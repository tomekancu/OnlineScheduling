from typing import Callable
from enum import Enum

from models import Task


# wklesla
def concave_function(task: Task, n: int) -> float:
    return task.base_length / n


# wklesla splaszczona
def concave_flat_function(task: Task, n: int, beta: float = 0.5) -> float:
    b_max = task.base_length / task.min_resources
    return (1 - beta) * task.base_length / n + beta * b_max


# wklesla splaszczona
def concave_fast_function(task: Task, n: int, beta: float = 2) -> float:
    return task.base_length / (beta * n)


# liniowa
def linear_function(task: Task, n: int) -> float:
    b_max = task.base_length / task.min_resources
    b_min = task.base_length / task.max_resources
    len_by_proc = (b_max - b_min) / (task.max_resources - task.min_resources)
    how_shorter = (n - task.min_resources) * len_by_proc
    return b_max - how_shorter


# wypukla
def convex_function(task: Task, n: int) -> float:
    b = task.base_length
    n_max = task.max_resources
    n_min = task.min_resources
    return b / (n - (n_min + n_max)) + b / n_max + b / n_min


class LengthFunctionType(Enum):
    CONCAVE = ("CONCAVE", concave_function)
    CONCAVE_FLAT = ("CONCAVE_FLAT", concave_flat_function)
    CONCAVE_FAST = ("CONCAVE_FAST", concave_fast_function)
    LINEAR = ("LINEAR", linear_function)
    CONVEX = ("CONVEX", convex_function)

    def __str__(self):
        return self.get_name()

    def __hash__(self):
        return hash(self.value[0])

    def __eq__(self, other):
        return self.value[0] == other.value[0]

    def __lt__(self, other):
        return self.value[0] < other.value[0]

    def __gt__(self, other):
        return self.value[0] > other.value[0]

    def get_name(self) -> str:
        return self.value[0]

    def get_function(self) -> Callable[[Task, int], float]:
        return self.value[1]
