from typing import List
import matplotlib.pyplot as plt

from schedulers.models import Procesor
from task import Task


class AbstractScheduler:

    def __init__(self):
        self.procesors: List[Procesor] = []
        self.clock: float = 0

    def reset(self, n_of_procesors):
        self.procesors = [Procesor(i) for i in range(n_of_procesors)]
        self.clock = 0

    def schedule(self, n_of_procesors: int, tasks: List[Task]):
        self.reset(n_of_procesors)
        tasks = sorted(tasks, key=lambda x: x.ready)
        for task in tasks:
            next_free_events = self.free_events(task.ready)
            for event in next_free_events:
                self.clock = event
                self.on_proc_free_event(event)

            self.clock = task.ready
            self.on_new_task_event(self.clock, task)

        next_free_events = self.free_events()
        while len(next_free_events) > 0:
            for event in next_free_events:
                self.clock = event
                self.on_proc_free_event(event)
            next_free_events = self.free_events()

    def free_events(self, max_time: float = None) -> List[float]:
        events = sorted(list(set(x.get_next_free_time() for x in self.procesors)))
        events = [event for event in events if self.clock < event]
        if max_time is not None:
            events = [event for event in events if event <= max_time]
        return events

    def on_new_task_event(self, clock: float, new_task: Task):
        pass

    def on_proc_free_event(self, clock: float):
        pass


def print_scheduling(scheduling: List[Procesor]):
    colors = ['orange', 'blue', 'red', 'yellow', 'green', 'purple', 'pink', 'gray']
    fig, gnt = plt.subplots()
    gnt.grid(True)
    gnt.set_ylabel('Processor')
    gnt.set_ylim(0, 10 * len(scheduling))

    gnt.set_yticks([5 + 10 * i for i in range(len(scheduling))])
    gnt.set_yticklabels([proc.id for proc in reversed(scheduling)])

    for i, proc in enumerate(reversed(scheduling)):
        for j, task in enumerate(proc.tasks):
            t_id = task.task.id
            color = colors[t_id % len(colors)]
            gnt.broken_barh([(task.start, task.end - task.start)], (0.5 + 10 * i, 9), facecolors=color, label=str(t_id))

    plt.savefig("output/gantt.png")
