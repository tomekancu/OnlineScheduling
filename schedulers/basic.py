from typing import List, DefaultDict, Set, Optional
from collections import defaultdict
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import copy

from schedulers.models import Procesor
from task import Task


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

    def get_title(self) -> str:
        name = self.__class__.__name__
        return f"{name} load:{self.load}"


def print_schedulings(instance: List[Task], schedulings: List[AbstractScheduler], file="gantt.png"):
    fig, axs = plt.subplots(nrows=len(schedulings), sharex='all', squeeze=False)
    fig.subplots_adjust(top=0.85, hspace=0.7)
    for i in range(len(schedulings)):
        title = schedulings[i].get_title()
        scheduling = schedulings[i].procesors
        ax = axs[i, 0]
        plot_scheduling(ax, instance, scheduling, title)
    fig.savefig(f"output/{file}")


def plot_scheduling(ax: Axes, instance: List[Task], scheduling: List[Procesor], name: Optional[str] = None):
    colors = ['orange', 'blue', 'red', 'yellow', 'green', 'purple', 'pink', 'gray']
    if name is not None:
        ax.set_title(name)
    ax.grid(True)

    ax.set_xlabel('Time')
    ax.set_ylabel('Processor')
    ax.set_ylim(0, 10 * len(scheduling))
    ax.set_yticks([5 + 10 * i for i in range(len(scheduling))])
    ax.set_yticklabels([proc.id for proc in reversed(scheduling)])

    for i, proc in enumerate(reversed(scheduling)):
        for j, task in enumerate(proc.tasks):
            t_id = task.task.id
            color = colors[t_id % len(colors)]
            ax.broken_barh([(task.start, task.end - task.start)], (0.5 + 10 * i, 9), facecolors=color, label=str(t_id))
            ax.annotate(str(t_id), xy=(task.start, 9.5 + 10 * i), xycoords='data',
                        horizontalalignment='left', verticalalignment='top')

    starts: DefaultDict[float, Set[int]] = defaultdict(set)
    for task in instance:
        starts[task.ready].add(task.id)
    ticks_ready_time = sorted(starts.keys())
    labels_ready_time = [str(starts[x]) for x in ticks_ready_time]

    ax2 = ax.twiny()
    ax2.set_xlabel('Tasks with ready time')
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(ticks_ready_time)
    ax2.set_xticklabels(labels_ready_time)
