from typing import List, DefaultDict, Set, Optional
from collections import defaultdict
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


def print_scheduling(instance: List[Task], scheduling: List[Procesor]):
    colors = ['orange', 'blue', 'red', 'yellow', 'green', 'purple', 'pink', 'gray']
    fig, gnt = plt.subplots()
    gnt.grid(True)

    gnt.set_xlabel('Time')
    gnt.set_ylabel('Processor')
    gnt.set_ylim(0, 10 * len(scheduling))
    gnt.set_yticks([5 + 10 * i for i in range(len(scheduling))])
    gnt.set_yticklabels([proc.id for proc in reversed(scheduling)])

    for i, proc in enumerate(reversed(scheduling)):
        for j, task in enumerate(proc.tasks):
            t_id = task.task.id
            color = colors[t_id % len(colors)]
            gnt.broken_barh([(task.start, task.end - task.start)], (0.5 + 10 * i, 9), facecolors=color, label=str(t_id))
            gnt.annotate(str(t_id), xy=(task.start, 9.5 + 10 * i), xycoords='data',
                         horizontalalignment='left', verticalalignment='top')

    starts: DefaultDict[float, Set[int]] = defaultdict(set)
    for task in instance:
        starts[task.ready].add(task.id)
    ticks_ready_time = sorted(starts.keys())
    labels_ready_time = [str(starts[x]) for x in ticks_ready_time]

    ax2 = gnt.twiny()
    ax2.set_xlabel('Tasks with ready time')
    ax2.set_xlim(gnt.get_xlim())
    ax2.set_xticks(ticks_ready_time)
    ax2.set_xticklabels(labels_ready_time)

    plt.savefig("output/gantt.png")
