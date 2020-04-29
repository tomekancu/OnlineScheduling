from models import Task
from schedulers.abstract_separate import AbstractSeparateScheduler
from schedulers.get_max import GetMaxScheduler


class SITAScheduler(AbstractSeparateScheduler):

    def __init__(self, task_size_treshold: float, proc_of_small: float = 0.5):
        super().__init__(task_size_treshold, proc_of_small)
        self.scheduler_for_small = GetMaxScheduler()
        self.scheduler_for_big = GetMaxScheduler()

    def get_title(self) -> str:
        return f"Base SITA $\\alpha={self.proc_of_small}$"

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
