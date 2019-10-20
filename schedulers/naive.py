from typing import List

from schedulers.basic import AbstractScheduler
from schedulers.models import ExecutingTask
from task import Task


class NaiveScheduler(AbstractScheduler):

    def __init__(self):
        super().__init__()
        self.queue: List[Task] = []

    def reset(self, n_of_procesors):
        super().reset(n_of_procesors)
        self.queue = []

    def on_new_task_event(self, clock: float, new_task: Task):
        self.queue.append(new_task)
        self.try_execute_queue(clock)

    def on_proc_free_event(self, clock: float):
        self.try_execute_queue(clock)

    def try_execute_queue(self, clock: float):
        while len(self.queue) > 0:
            free_procesors = [p for p in self.procesors if p.is_free(clock)]
            if len(free_procesors) < self.queue[0].min_resources:
                return
            task = self.queue.pop(0)
            free_procesors = free_procesors[:task.max_resources]

            assigned_resources = len(free_procesors)
            length = task.calc_length(assigned_resources)
            end = clock + length
            executing_task = ExecutingTask(task, clock, end, assigned_resources)

            for p in free_procesors:
                p.add_task(executing_task)
