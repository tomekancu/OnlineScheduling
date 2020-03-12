from schedulers.abstract import AbstractScheduler
from models import Task


class GetMaxScheduler(AbstractScheduler):

    def __init__(self):
        super().__init__()

    def on_new_task_event(self, clock: float, new_task: Task):
        self.queue.append(new_task)
        self.try_execute_queue(clock)

    def on_proc_free_event(self, clock: float):
        self.try_execute_queue(clock)

    def try_execute_queue(self, clock: float):
        free_procesors = [p for p in self.procesors if p.is_free(clock)]
        while True:
            task = next((t for t in self.queue
                         if min(t.max_resources, len(self.procesors)) <= len(free_procesors)
                         and t.min_resources <= len(free_procesors)), None)
            if task is None:
                break

            assigned_resources = free_procesors[:task.max_resources]
            del free_procesors[:task.max_resources]

            self.start_task(task, assigned_resources, clock)
