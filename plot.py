from collections import defaultdict
from typing import List, Optional, DefaultDict, Set, Dict, Callable

from matplotlib import pyplot as plt
from matplotlib.axes import Axes

from schedulers.abstract import AbstractScheduler
from metrics import Metrics, get_max_end
from models import Task, Procesor


def print_schedulings(instance: List[Task], schedulings: List[AbstractScheduler], file="gantt.png"):
    height = 3.8 * len(schedulings)
    fig, axs = plt.subplots(nrows=len(schedulings), sharex='all', squeeze=False, figsize=(6.4, height))
    fig.tight_layout(pad=2.5, h_pad=8, rect=(0, 0, 1, (height - 0.7) / height))
    xmax = max(get_max_end(s.procesors) for s in schedulings) + 1
    for i in range(len(schedulings)):
        m = schedulings[i].calc_metrics()
        title = schedulings[i].get_title() + "\n" + str(m)
        scheduling = schedulings[i].procesors
        ax = axs[i, 0]
        plot_scheduling(ax, instance, scheduling, xmax, title)
    fig.savefig(f"output/{file}")


def plot_scheduling(ax: Axes, instance: List[Task], scheduling: List[Procesor], xmax: float,
                    name: Optional[str] = None):
    colors = ['orange', 'blue', 'red', 'yellow', 'green', 'purple', 'pink', 'gray']
    if name is not None:
        ax.set_title(name)
    ax.grid(True)

    ax.set_xlim(-1, xmax)
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


def _to_plot(xs_of_metrics: Dict[float, Dict[str, Metrics]], func: Callable[[Metrics], float]):
    xs = list(sorted(xs_of_metrics.keys()))
    plots = defaultdict(lambda: [])
    for x in xs:
        for name, metric in xs_of_metrics[x].items():
            plots[name].append(func(metric))
    return plots


def print_metrics(xs_of_metrics: Dict[float, Dict[str, Metrics]], name, file="metrics.png"):
    fig, axs = plt.subplots(nrows=2, ncols=3, squeeze=False, figsize=(12, 8))
    fig.suptitle(name)
    fig.tight_layout(pad=3, h_pad=3)

    xs = list(sorted(xs_of_metrics.keys()))

    i = 0
    for name, func in {"mean response time": lambda x: x.mean_response_time,
                       "mean processing time": lambda x: x.mean_processing_time,
                       "mean ideal delay time": lambda x: x.mean_ideal_delay_time,
                       "processing time to\n response time": lambda x: x.processing_time_to_response_time,
                       "delay time to\n response time": lambda x: x.delay_time_to_response_time,
                       "actual resource load": lambda x: x.actual_resource_load}.items():
        plots = _to_plot(xs_of_metrics, func)
        axs[i // 3, i % 3].set_title(name)
        for name_ske, ys in plots.items():
            axs[i // 3, i % 3].plot(xs, ys, label=name_ske)
        i += 1

    handles, labels = axs[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3)

    fig.savefig(f"output/{file}")
