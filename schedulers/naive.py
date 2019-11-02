from typing import List

from schedulers.basic import AbstractScheduler
from schedulers.models import ExecutingTask
from task import Task


class NaiveScheduler(AbstractScheduler):

    def __init__(self, load: float = 0):
        super().__init__(load)
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
        while True:
            free_procesors = [p for p in self.procesors if p.is_free(clock)]
            task_can_be_begin = [t for t in self.queue
                                 if min(t.max_resources, len(self.procesors)) <= len(free_procesors)
                                 and t.min_resources <= len(free_procesors)]
            if len(task_can_be_begin) == 0:
                break

            task = min(task_can_be_begin, key=lambda x: self.calc_length(x, len(free_procesors)))

            assigned_resources = free_procesors[:task.max_resources]

            a_r = len(assigned_resources)
            length = self.calc_length(task, a_r)
            end = clock + length
            task.parts.append(1.0)
            executing_task = ExecutingTask(task, clock, end, length)
            for p in assigned_resources:
                p.add_task(executing_task)
            self.queue.remove(task)
