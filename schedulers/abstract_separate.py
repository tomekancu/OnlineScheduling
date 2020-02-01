from typing import Callable, Any

from models import Task
from schedulers.abstract import AbstractScheduler, comparator_smallest_task


class AbstractSeparateScheduler(AbstractScheduler):

    def __init__(self, task_size_treshold: float, proc_of_small: float = 0.5,
                 priority_function: Callable[[AbstractScheduler, Task, int], Any] = comparator_smallest_task):
        super().__init__(priority_function)
        self.task_size_treshold = task_size_treshold
        self.proc_of_small = proc_of_small

    def get_name(self) -> str:
        return super().get_name() + "-" + str(self.proc_of_small)

    def get_title(self) -> str:
        return super().get_title() + f" thres:{self.task_size_treshold} " \
                                     f"small:{self.proc_of_small}:{self.get_n_of_proc_small()}"

    def get_n_of_proc_small(self) -> int:
        calc_proc_small = int(len(self.procesors) * self.proc_of_small)
        return max(1, min(len(self.procesors) - 1, calc_proc_small))

    def is_big_task(self, task: Task) -> bool:
        return task.base_length > self.task_size_treshold
