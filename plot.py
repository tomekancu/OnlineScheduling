from collections import defaultdict
from typing import List, Optional, DefaultDict, Set

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from schedulers.abstract import AbstractScheduler
from models import Task, Procesor


def print_schedulings(instance: List[Task], schedulings: List[AbstractScheduler], file="gantt.png"):
    fig, axs = plt.subplots(nrows=len(schedulings), sharex='all', squeeze=False)
    fig.subplots_adjust(top=0.85-0.05, hspace=0.7+0.25)
    for i in range(len(schedulings)):
        m = schedulings[i].calc_metrics()
        title = schedulings[i].get_title() + "\n" + str(m)
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