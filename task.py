from typing import Callable
import math
from pprint import pprint


class Task:

    def __init__(self, i: int, ready: int, min_resources: int, max_resources: int, base_lenght: int,
                 length_function: Callable[['Task', int], int]):
        self.id = i
        self.ready = ready
        self.min_resources = min_resources
        self.max_resources = max_resources
        self.base_length = base_lenght
        self.cost_function = length_function

        self.real_length = None
        self.assigned_resources = None
        self.start_time = None
        self.end_time = None

    def __str__(self) -> str:
        # return f"Task({self.id}, {self.ready}, {self.min_resources}, {self.max_resources}, {self.base_length})"
        return str(vars(self))

    def calc_length(self, procs) -> int:
        return int(math.ceil(self.cost_function(self, procs)))


