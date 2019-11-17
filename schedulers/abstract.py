from typing import List, Optional
import copy

from metrics import Metrics, get_metrics
from models import Procesor, Task


class AbstractScheduler:

    def __init__(self, load: float = 0):
        self.procesors: List[Procesor] = []
        self.clock: float = 0
        self.load = load

    def calc_length(self, task: Task, given_procesors: int):
        scale_length = 1 / (1 - self.load)
        return scale_length * task.calc_length(given_procesors)

    def reset(self, n_of_procesors):
        self.procesors = [Procesor(i) for i in range(n_of_procesors)]
        self.clock = 0

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

    def free_events(self, max_time: Optional[float] = None) -> List[float]:
        events = set(x.get_next_free_time() for x in self.procesors)
        events = [event for event in events if self.clock < event]
        if max_time is not None:
            events = [event for event in events if event <= max_time]
        return sorted(events)

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

    def calc_metrics(self) -> Metrics:
        return get_metrics(self.procesors)

    def get_name(self) -> str:
        return self.__class__.__name__

    def get_title(self) -> str:
        return f"{self.get_name()} load:{self.load}"
