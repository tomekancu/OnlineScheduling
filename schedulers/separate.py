from typing import Callable, Any

from schedulers.abstract_separate import AbstractSeparateScheduler
from schedulers.abstract import AbstractScheduler, comparator_smallest_task
from schedulers.naive import NaiveScheduler
from models import Task


class SeparateScheduler(AbstractSeparateScheduler):

    def __init__(self, task_size_treshold: float, proc_of_small: float = 0.5,
                 priority_function: Callable[[AbstractScheduler, Task, int], Any] = comparator_smallest_task):
        super().__init__(task_size_treshold, proc_of_small, priority_function)
        self.scheduler_for_small = NaiveScheduler(self.priority_function)
        self.scheduler_for_big = NaiveScheduler(self.priority_function)

    def reset(self, n_of_procesors):
        super().reset(n_of_procesors)
        n_of_proc_for_small = self.get_n_of_proc_small()
        self.scheduler_for_small.reset(n_of_proc_for_small)
        self.scheduler_for_big.reset(n_of_procesors - n_of_proc_for_small)

        self.scheduler_for_small.procesors = self.procesors[:n_of_proc_for_small]
        self.scheduler_for_big.procesors = self.procesors[n_of_proc_for_small:]

    def on_new_task_event(self, clock: float, new_task: Task):
        if self.is_big_task(new_task):
            self.scheduler_for_big.on_new_task_event(clock, new_task)
        else:
            self.scheduler_for_small.on_new_task_event(clock, new_task)

    def on_proc_free_event(self, clock: float):
        self.scheduler_for_small.on_proc_free_event(clock)
        self.scheduler_for_big.on_proc_free_event(clock)
