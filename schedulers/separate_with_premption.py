from typing import List

from schedulers.abstract import AbstractScheduler
from models import Task, ExecutingTask, Procesor


class SeparateWithPremptionScheduler(AbstractScheduler):

    def __init__(self, task_size_treshold: float, proc_of_small: float = 0.5, load: float = 0):
        super().__init__(load)
        self.queue: List[Task] = []
        self.task_size_treshold = task_size_treshold
        self.proc_of_small = proc_of_small
        self.procesors_for_small: List[Procesor] = []
        self.procesors_for_big: List[Procesor] = []

    def get_n_of_proc_small(self) -> int:
        calc_proc_small = int(len(self.procesors) * self.proc_of_small)
        return max(1, min(len(self.procesors) - 1, calc_proc_small))

    def reset(self, n_of_procesors):
        super().reset(n_of_procesors)
        self.queue = []
        n_of_proc_for_small = self.get_n_of_proc_small()
        self.procesors_for_small = self.procesors[:n_of_proc_for_small]
        self.procesors_for_big = self.procesors[n_of_proc_for_small:]

    def is_big_task(self, task: Task) -> bool:
        return task.base_length > self.task_size_treshold

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

    def get_name(self) -> str:
        return super().get_name() + str(self.proc_of_small)

    def get_title(self) -> str:
        return super().get_title() + f" thres:{self.task_size_treshold} " \
                                     f"small:{self.proc_of_small}:{self.get_n_of_proc_small()}"
