import math
from typing import List, Optional, Callable


class Task:

    def __init__(self, i: int, ready: float, min_resources: int, max_resources: int, base_lenght: float,
                 length_function: Callable[['Task', int], float]):
        self.id = i
        self.ready = ready
        self.min_resources = min_resources
        self.max_resources = max_resources
        self.base_length = base_lenght
        self.cost_function = length_function
        self.parts: List[float] = []

    def __str__(self) -> str:
        return f"Task(id:{self.id}, ready:{self.ready}, base:{self.base_length}, min:{self.min_resources}, " \
               f"max:{self.max_resources})"

    def calc_length(self, procs) -> float:
        if procs < self.min_resources:
            return math.inf
        if procs > self.max_resources:
            return self.cost_function(self, self.max_resources)
        return self.cost_function(self, procs)

    def done_part(self) -> float:
        return sum(self.parts)

    def left_part(self) -> float:
        return 1 - self.done_part()


class ExecutingTask:

    def __init__(self, task: Task, start: float, end: float, initial_length: float):
        self.task = task
        self.start = start
        self.end = end
        self.initial_length = initial_length

    def __str__(self) -> str:
        return f"ExecutingTask(start:{self.start}, end:{self.end}, task:{self.task})"

    def busy(self) -> float:
        return self.end - self.start

    def done_part(self) -> float:
        return self.busy() / self.initial_length


class Procesor:

    def __init__(self, i: int, tasks: Optional[List[ExecutingTask]] = None):
        self.id = i
        if tasks is None:
            tasks = []
        self.tasks: List[ExecutingTask] = tasks

    def __str__(self) -> str:
        return f"Procesor(id:{self.id}, taks:{self.tasks})"

    def add_task(self, task: ExecutingTask):
        if len(self.tasks) > 0:
            last_task = self.tasks[-1]
            assert last_task.end <= task.start
        self.tasks.append(task)

    def get_next_free_time(self) -> float:
        if len(self.tasks) == 0:
            return 0.0
        last_task = self.tasks[-1]
        return last_task.end

    def is_free(self, when: float) -> bool:
        return self.get_next_free_time() <= when

    def get_last_task(self) -> Optional[ExecutingTask]:
        if len(self.tasks) == 0:
            return None
        return self.tasks[-1]

    def get_last_doing_task(self, when: float) -> Optional[ExecutingTask]:
        if self.is_free(when):
            return None
        return self.get_last_task()
