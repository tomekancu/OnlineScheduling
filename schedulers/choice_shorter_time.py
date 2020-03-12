from collections import defaultdict
from typing import List, Tuple

from models import Task, Procesor
from schedulers.abstract import AbstractScheduler


class ChoiceShorterTimeScheduler(AbstractScheduler):

    def __init__(self):
        super().__init__()

    def on_new_task_event(self, clock: float, new_task: Task):
        free_procesors_now = [p for p in self.procesors if p.is_free(clock)]
        if len(free_procesors_now) < new_task.min_resources:
            self.queue.append(new_task)
            return
        if self.should_be_run_now(clock, new_task, free_procesors_now):
            assigned_resources = free_procesors_now[:new_task.max_resources]
            del free_procesors_now[:new_task.max_resources]
            self.start_task(new_task, assigned_resources, clock)
        else:
            self.queue.append(new_task)

    def should_be_run_now(self, clock: float, task: Task, free_procesors_now: List[Procesor]) -> bool:
        complete_time_if_now = clock + task.calc_real_length(len(free_procesors_now))
        for later, free_procesors_later in self.get_next_free_events_with_proc_num(clock):
            complete_time_if_later = later + task.calc_real_length(free_procesors_later)
            if complete_time_if_later < complete_time_if_now:
                return False
            if free_procesors_later >= task.max_resources:
                break
        return True

    def get_next_free_events_with_proc_num(self, after: float) -> List[Tuple[float, int]]:
        tups = []
        def_dict = defaultdict(lambda: 0)
        for proc in self.procesors:
            free_time = proc.get_next_free_time()
            def_dict[free_time] += 1
        prev_sum = 0
        for key in sorted(def_dict.keys()):
            prev_sum += def_dict[key]
            if key > after:
                tups.append((key, prev_sum))
        return tups

    def on_proc_free_event(self, clock: float):
        free_procesors = [p for p in self.procesors if p.is_free(clock)]
        while True:
            task_mins = [t for t in self.queue if t.min_resources <= len(free_procesors)]

            task = next((t for t in task_mins
                         if min(t.max_resources, len(self.procesors)) <= len(free_procesors)), None)
            if task is None:
                task = next(iter(task_mins), None)
                if task is None:
                    return
                if not self.should_be_run_now(clock, task, free_procesors):
                    return

            assigned_resources = free_procesors[:task.max_resources]
            del free_procesors[:task.max_resources]

            self.start_task(task, assigned_resources, clock)
