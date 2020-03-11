import copy
from typing import List, Optional, Any, Callable

from metrics import Metrics, make_metrics
from models import Procesor, Task, ExecutingTask


class AbstractScheduler:

    def __init__(self, priority_function: Optional[Callable[['AbstractScheduler', Task, int], Any]]):
        self.priority_function = priority_function
        self.procesors: List[Procesor] = []
        self.clock: float = 0
        self.queue: List[Task] = []

    def get_name(self) -> str:
        priority_function_name = ""
        if self.priority_function is not None:
            priority_function_name = self.priority_function.__name__
        return f"{self.__class__.__name__}-{priority_function_name}"

    def get_title(self) -> str:
        priority_function_name = ""
        if self.priority_function is not None:
            priority_function_name = self.priority_function.__name__
        return f"{self.__class__.__name__} {priority_function_name}"

    def reset(self, n_of_procesors):
        self.procesors = [Procesor(i) for i in range(n_of_procesors)]
        self.clock = 0
        self.queue = []

    def schedule(self, n_of_procesors: int, tasks: List[Task]):
        tasks = copy.deepcopy(tasks)
        self.reset(n_of_procesors)
        tasks = sorted(tasks, key=lambda x: x.ready)
        for task in tasks:
            next_free_event = self.next_free_event(task.ready)
            while next_free_event is not None:
                self.clock = next_free_event
                self.on_proc_free_event(next_free_event)
                next_free_event = self.next_free_event(task.ready)

            self.clock = task.ready
            self.on_new_task_event(self.clock, task)

        next_free_event = self.next_free_event()
        while next_free_event is not None:
            self.clock = next_free_event
            self.on_proc_free_event(next_free_event)
            next_free_event = self.next_free_event()

        for task in tasks:
            assert task.is_finished()

    def next_free_event(self, max_time: Optional[float] = None) -> Optional[float]:
        events = set(x.get_next_free_time() for x in self.procesors)
        events = [event for event in events if self.clock < event]
        if max_time is not None:
            events = [event for event in events if event <= max_time]
        if len(events) == 0:
            return None
        return min(events)

    def on_new_task_event(self, clock: float, new_task: Task):
        pass

    def on_proc_free_event(self, clock: float):
        pass

    def start_task(self, t: Task, assigned_resources: List[Procesor], start: float):
        a_r = len(assigned_resources)
        assert a_r >= t.min_resources
        left = t.left_part()
        length = t.calc_length(a_r) * left
        t.parts.append(left)
        executing_task = ExecutingTask(t, start, length)
        for p in assigned_resources:
            p.add_task(executing_task)
        if t in self.queue:
            self.queue.remove(t)

    def stop_running_tasks(self, when: float) -> List[Task]:
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

    def stop_running_tasks_and_add_to_queue(self, when: float):
        stoped_tasks = self.stop_running_tasks(when)
        self.queue = stoped_tasks + self.queue

    def calc_metrics(self) -> Metrics:
        return make_metrics(self.procesors)


"""
minimalizacja pracochłonności
"""


def comparator_oldest_task(scheduler: AbstractScheduler, task: Task, posible_procesors: int) -> Any:
    return task.ready


def comparator_smallest_task(scheduler: AbstractScheduler, task: Task, posible_procesors: int) -> Any:
    return task.calc_length(posible_procesors)


def comparator_smallest_left_task(scheduler: AbstractScheduler, task: Task, posible_procesors: int) -> Any:
    return task.calc_real_length(posible_procesors)
