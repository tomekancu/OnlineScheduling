from schedulers.abstract import AbstractScheduler
from schedulers.naive import NaiveScheduler
from models import Task


class SeparateScheduler(AbstractScheduler):

    def __init__(self, task_size_treshold: float, proc_of_small: float = 0.5):
        super().__init__()
        self.task_size_treshold = task_size_treshold
        self.proc_of_small = proc_of_small
        self.scheduler_for_small = NaiveScheduler()
        self.scheduler_for_big = NaiveScheduler()

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
        self.scheduler_for_small.reset(n_of_proc_for_small)
        self.scheduler_for_big.reset(n_of_procesors - n_of_proc_for_small)

        self.scheduler_for_small.procesors = self.procesors[:n_of_proc_for_small]
        self.scheduler_for_big.procesors = self.procesors[n_of_proc_for_small:]

    def is_big_task(self, task: Task) -> bool:
        return task.base_length > self.task_size_treshold

    def on_new_task_event(self, clock: float, new_task: Task):
        if self.is_big_task(new_task):
            self.scheduler_for_big.on_new_task_event(clock, new_task)
        else:
            self.scheduler_for_small.on_new_task_event(clock, new_task)

    def on_proc_free_event(self, clock: float):
        self.scheduler_for_small.on_proc_free_event(clock)
        self.scheduler_for_big.on_proc_free_event(clock)
