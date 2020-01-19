from typing import List

from schedulers.abstract import AbstractScheduler
from models import Task, Procesor


class SeparateWithPremptionScheduler(AbstractScheduler):

    def __init__(self, task_size_treshold: float, proc_of_small: float = 0.5, load: float = 0):
        super().__init__(load)
        self.task_size_treshold = task_size_treshold
        self.proc_of_small = proc_of_small
        self.procesors_for_small: List[Procesor] = []
        self.procesors_for_big: List[Procesor] = []

    def get_name(self) -> str:
        return super().get_name() + str(self.proc_of_small)

    def get_title(self) -> str:
        return super().get_title() + f" thres:{self.task_size_treshold} " \
                                     f"small:{self.proc_of_small}:{self.get_n_of_proc_small()}"

    def get_n_of_proc_small(self) -> int:
        calc_proc_small = int(len(self.procesors) * self.proc_of_small)
        return max(1, min(len(self.procesors) - 1, calc_proc_small))

    def reset(self, n_of_procesors):
        super().reset(n_of_procesors)
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
        self.stop_running_tasks_and_add_to_queue(clock)
        free_procesors_in_small = [p for p in self.procesors_for_small if p.is_free(clock)]
        free_procesors_in_big = [p for p in self.procesors_for_big if p.is_free(clock)]

        assigned = []
        left_small_procs = len(free_procesors_in_small)
        left_big_procs = len(free_procesors_in_big)
        task_can_be_begin_in_small = self.get_task_can_be_begin(False, left_small_procs)
        task_can_be_begin_in_big = self.get_task_can_be_begin(True, left_big_procs)
        while len(task_can_be_begin_in_small) > 0:
            task_in_small = min(task_can_be_begin_in_small, key=lambda x: self.calc_length(x, left_small_procs))
            taken_small_number = min(task_in_small.max_resources, left_small_procs)
            assigned.append((task_in_small, taken_small_number, 0))
            self.queue.remove(task_in_small)
            left_small_procs -= taken_small_number
            task_can_be_begin_in_small = self.get_task_can_be_begin(False, left_small_procs)
        while len(task_can_be_begin_in_big) > 0:
            task_in_big = min(task_can_be_begin_in_big, key=lambda x: self.calc_length(x, left_big_procs))
            taken_big_number = min(task_in_big.max_resources, left_big_procs)
            assigned.append((task_in_big, 0, taken_big_number))
            self.queue.remove(task_in_big)
            left_big_procs -= taken_big_number
            task_can_be_begin_in_big = self.get_task_can_be_begin(True, left_big_procs)
        if left_small_procs + left_big_procs > 0:
            for i, (t, smalls, bigs) in enumerate(assigned):
                to_more_assigned = t.max_resources - (smalls + bigs)
                if to_more_assigned <= 0:
                    continue

                added_smalls = min(left_small_procs, to_more_assigned)
                to_more_assigned -= added_smalls
                added_bigs = min(left_big_procs, to_more_assigned)

                smalls += added_smalls
                bigs += added_bigs

                assigned[i] = (t, smalls, bigs)

                left_small_procs -= added_smalls
                left_big_procs -= added_bigs

                if left_small_procs + left_big_procs == 0:
                    break
        if left_small_procs + left_big_procs > 0:
            task_can_be_begin = self.get_all_task_can_be_begin(left_small_procs + left_big_procs)
            while len(task_can_be_begin) > 0:
                task = min(task_can_be_begin, key=lambda x: self.calc_length(x, left_small_procs + left_big_procs))
                taken_small_number = min(task.max_resources, left_small_procs)
                taken_big_number = min(task.max_resources - taken_small_number, left_big_procs)
                assigned.append((task, taken_small_number, taken_big_number))
                self.queue.remove(task)
                left_small_procs -= taken_small_number
                left_big_procs -= taken_big_number
                task_can_be_begin = self.get_all_task_can_be_begin(left_small_procs + left_big_procs)

        for t, smalls, bigs in assigned:
            assigned_resources = []
            assigned_resources += free_procesors_in_small[:smalls]
            del free_procesors_in_small[:smalls]
            assigned_resources += free_procesors_in_big[:bigs]
            del free_procesors_in_big[:bigs]
            self.start_task(t, assigned_resources, clock)

    def get_all_task_can_be_begin(self, available_processors_number: int):
        return [t for t in self.queue
                if t.min_resources <= available_processors_number]

    def get_task_can_be_begin(self, big: bool, available_processors_number: int):
        return [t for t in self.queue
                if ((big and self.is_big_task(t)) or (not big and not self.is_big_task(t)))
                and t.min_resources <= available_processors_number]
