from typing import Callable, Any

from schedulers.abstract import AbstractScheduler, comparator_smallest_task
from models import Task


class NaiveScheduler(AbstractScheduler):

    def __init__(self, priority_function: Callable[[AbstractScheduler, Task, int], Any] = comparator_smallest_task):
        super().__init__()
        self.priority_function = priority_function

    def get_name(self) -> str:
        return super().get_name() + f"-{self.priority_function.__name__}"

    def get_title(self) -> str:
        return super().get_title() + f" {self.priority_function.__name__}"

    def on_new_task_event(self, clock: float, new_task: Task):
        self.queue.append(new_task)
        self.try_execute_queue(clock)

    def on_proc_free_event(self, clock: float):
        self.try_execute_queue(clock)

    def try_execute_queue(self, clock: float):
        free_procesors = [p for p in self.procesors if p.is_free(clock)]
        while True:
            task_can_be_begin = [t for t in self.queue
                                 if min(t.max_resources, len(self.procesors)) <= len(free_procesors)
                                 and t.min_resources <= len(free_procesors)]
            if len(task_can_be_begin) == 0:
                break

            task = min(task_can_be_begin, key=lambda x: self.priority_function(self, x, len(free_procesors)))

            assigned_resources = free_procesors[:task.max_resources]
            del free_procesors[:task.max_resources]

            self.start_task(task, assigned_resources, clock)
