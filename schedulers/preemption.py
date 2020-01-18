from typing import List, Set
import math

from schedulers.abstract import AbstractScheduler
from models import ExecutingTask, Procesor, Task


class PreemptionScheduler(AbstractScheduler):

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
        stoped_tasks = self._stop_executing_tasks(clock)
        self.queue = stoped_tasks + self.queue

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

                self._start_task(t, assigned_resources, clock)

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

            self._start_task(t, assigned_resources, clock)

    def _get_tasks_to_do(self) -> List[Task]:
        task_to_finish = sorted(self.queue, key=lambda x: x.ready)
        task_can_be_begin = []
        sum_min_proc = 0
        for t in task_to_finish:
            sum_min_proc += t.min_resources
            if sum_min_proc > len(self.procesors):
                break
            task_can_be_begin.append(t)
        return task_can_be_begin

    def _stop_executing_tasks(self, when: float) -> List[Task]:
        change_part_task = set()
        for p in self.procesors:
            executing_task = p.get_last_doing_task(when)
            if executing_task is None:
                continue

            executing_task.end = when

            if executing_task.task in change_part_task:
                continue

            done_part = executing_task.done_part()
            executing_task.task.parts[-1] *= done_part
            change_part_task.add(executing_task.task)
        return list(filter(lambda t: not t.is_finished(), change_part_task))

    def _start_task(self, t: Task, assigned_resources: List[Procesor], start: float):
        a_r = len(assigned_resources)
        left = t.left_part()
        length = self.calc_length(t, a_r) * left
        end = start + length
        t.parts.append(left)
        executing_task = ExecutingTask(t, start, end, length)
        for p in assigned_resources:
            p.add_task(executing_task)
        if t in self.queue:
            self.queue.remove(t)
