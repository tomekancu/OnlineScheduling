from typing import List
import math

from schedulers.abstract import AbstractScheduler, comparator_oldest_task
from models import Task


class PreemptionScheduler(AbstractScheduler):

    def __init__(self, load: float = 0):
        super().__init__(load)

    def on_new_task_event(self, clock: float, new_task: Task):
        self.queue.append(new_task)
        self.try_execute_queue(clock)

    def on_proc_free_event(self, clock: float):
        self.try_execute_queue(clock)

    def try_execute_queue(self, clock: float):
        self.stop_running_tasks_and_add_to_queue(clock)

        task_can_be_begin = self._get_tasks_to_do()

        if len(task_can_be_begin) == 0:
            return

        free_procesors = [p for p in self.procesors]

        # done all taks where max_resources <= to_assing
        while len(task_can_be_begin) > 0:
            to_assign = int(math.floor(len(free_procesors) / len(task_can_be_begin)))
            smaller_than_assign = 0
            for t in filter(lambda x: x.max_resources <= to_assign, task_can_be_begin):
                smaller_than_assign += 1
                task_can_be_begin.remove(t)

                assigned_resources = free_procesors[:t.max_resources]
                del free_procesors[:t.max_resources]

                self.start_task(t, assigned_resources, clock)

            if smaller_than_assign == 0:
                break

        if len(task_can_be_begin) == 0:
            return

        # done all task with assigned_resources, the oldest get +1
        to_assign = int(math.floor(len(free_procesors) / len(task_can_be_begin)))
        for i, t in enumerate(reversed(task_can_be_begin)):
            assigned = to_assign
            if i == len(task_can_be_begin) - 1:
                assigned = len(free_procesors)

            assigned_resources = free_procesors[:assigned]
            del free_procesors[:assigned]

            self.start_task(t, assigned_resources, clock)

    def _get_tasks_to_do(self) -> List[Task]:
        task_to_finish = sorted(self.queue, key=lambda x: comparator_oldest_task(self, x, len(self.procesors)))
        task_can_be_begin = []
        sum_min_proc = 0
        for t in task_to_finish:
            sum_min_proc += t.min_resources
            if sum_min_proc > len(self.procesors):
                break
            task_can_be_begin.append(t)
        return task_can_be_begin
