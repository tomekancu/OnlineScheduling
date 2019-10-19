from typing import Callable
import math


class Task:

    def __init__(self, i: int, ready: float, min_resources: int, max_resources: int, base_lenght: int,
                 length_function: Callable[['Task', int], float]):
        self.id = i
        self.ready = ready
        self.min_resources = min_resources
        self.max_resources = max_resources
        self.base_length = base_lenght
        self.cost_function = length_function

    def __str__(self) -> str:
        return f"Task(id:{self.id}, ready:{self.ready}, base:{self.base_length}, min:{self.min_resources}, " \
               f"max:{self.max_resources})"

    def calc_length(self, procs) -> float:
        if procs < self.min_resources:
            return math.inf
        if procs > self.max_resources:
            return self.cost_function(self, self.max_resources)
        return self.cost_function(self, procs)
