from schedulers.abstract import AbstractScheduler
from models import Task


class FairScheduler(AbstractScheduler):

    def __init__(self):
        super().__init__()

    def get_title(self) -> str:
        return "Fair"

    def on_new_task_event(self, clock: float, new_task: Task):
        self.queue.append(new_task)
        self.try_execute_queue(clock)

    def on_proc_free_event(self, clock: float):
        self.try_execute_queue(clock)

    def try_execute_queue(self, clock: float):
        self.stop_running_tasks_and_add_to_queue(clock)

        all_queed_task = sorted(self.queue, key=lambda x: (x.min_resources, x.ready, x.id))
        assigned = {}

        left_procs = len(self.procesors)
        task_can_be_begin = []
        for t in all_queed_task:
            if left_procs < t.min_resources:
                break
            left_procs -= t.min_resources
            assigned[t] = t.min_resources
            task_can_be_begin.append(t)

        while left_procs > 0 and len(task_can_be_begin) > 0:
            min_assigned = min(assigned[t] for t in task_can_be_begin)
            i = 0
            while i < len(task_can_be_begin):
                t = task_can_be_begin[i]
                asigned_to_t = assigned[t]
                if asigned_to_t >= t.max_resources:
                    del task_can_be_begin[i]
                    continue
                if asigned_to_t > min_assigned:
                    i += 1
                    continue
                assigned[t] += 1
                left_procs -= 1
                if left_procs <= 0:
                    break
                i += 1

        free_procesors = [p for p in self.procesors]
        for t, proc_num in assigned.items():
            assigned_resources = free_procesors[:proc_num]
            del free_procesors[:proc_num]
            self.start_task(t, assigned_resources, clock)
