from schedulers.abstract import AbstractScheduler, comparator_smallest_task
from models import Task


class NaiveScheduler(AbstractScheduler):

    def on_new_task_event(self, clock: float, new_task: Task):
        self.queue.append(new_task)
        self.try_execute_queue(clock)

    def on_proc_free_event(self, clock: float):
        self.try_execute_queue(clock)

    def try_execute_queue(self, clock: float):
        free_procesors = [p for p in self.procesors if p.is_free(clock)]
        while True:
            task_can_be_begin = [t for t in self.queue
                                 if min(t.max_resources, len(self.procesors)) <= len(free_procesors)
                                 and t.min_resources <= len(free_procesors)]
            if len(task_can_be_begin) == 0:
                break

            task = min(task_can_be_begin, key=lambda x: comparator_smallest_task(self, x, len(free_procesors)))

            assigned_resources = free_procesors[:task.max_resources]
            del free_procesors[:task.max_resources]

            self.start_task(task, assigned_resources, clock)
