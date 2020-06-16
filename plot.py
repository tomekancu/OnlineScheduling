from collections import defaultdict
from typing import List, Optional, DefaultDict, Set, Dict, Callable, Tuple, Any

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

    ax.set_xlim(0, xmax)
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


def _to_plot(xs_of_metrics: Dict[Any, Dict[str, Metrics]], func: Callable[[Metrics], float]):
    xs = list(sorted(xs_of_metrics.keys()))
    plots = defaultdict(lambda: [])
    for x in xs:
        for name, metric in xs_of_metrics[x].items():
            plots[name].append(func(metric))
    return plots


def print_metrics(xs_of_metrics: Dict[Any, Dict[str, Metrics]], main_name: str,
                  plot_names_mapping: Dict[str, str] = None, scheduler_names_mapping: Dict[str, str] = None,
                  file="metrics.png"):
    if plot_names_mapping is None:
        plot_names_mapping = {}
    if scheduler_names_mapping is None:
        scheduler_names_mapping = {}
    fig, axs = plt.subplots(nrows=3, ncols=3, squeeze=False, figsize=(12, 12))
    fig.suptitle(main_name)
    fig.tight_layout(pad=4, h_pad=3)

    xs = list(sorted(xs_of_metrics.keys()))
    xs = list(map(lambda x: x if isinstance(x, int) or isinstance(x, float) or isinstance(x, str) else str(x), xs))

    for i, (name, func) in enumerate(
            {"mean response time": lambda x: x.mean_response_time,
             "mean processing time": lambda x: x.mean_processing_time,
             "resource load": lambda x: x.resource_usage,
             "mean delay time": lambda x: x.mean_delay_time,
             "mean delay processing time": lambda x: x.mean_delay_processing_time,
             "mean ideal delay time": lambda x: x.mean_ideal_delay_time,
             "delay time to\n response time": lambda x: x.delay_time_to_response_time,
             "delay processing time to\n response time": lambda x: x.delay_processing_time_to_response_time,
             "ideal delay time to\n response time": lambda x: x.ideal_delay_time_to_response_time,
             }.items()):
        plots = _to_plot(xs_of_metrics, func)
        title = plot_names_mapping.get(name, name)
        axs[i // 3, i % 3].set_title(title)
        # axs[i // 3, i % 3].set_yscale('log')
        # axs[i // 3, i % 3].set_xscale('log')
        for name_ske, ys in plots.items():
            label = scheduler_names_mapping.get(name_ske, name_ske)
            axs[i // 3, i % 3].plot(xs, ys, label=label)

    handles, labels = axs[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3)

    fig.savefig(f"output/{file}")


def print_cost_functions(begin: int, end: int, base: int,
                         cost_functions_paris: List[Tuple[str, Callable[[Task, int], float]]],
                         file="cost.png"):
    fig, axs = plt.subplots()
    fig.suptitle("cost functions")
    for name, func in cost_functions_paris:
        t = Task(0, 0, begin, end, base, func)
        xs = list(range(t.min_resources, t.max_resources + 1))
        ys = [t.calc_length(x) for x in xs]
        axs.plot(xs, ys, label=name)
    fig.legend()
    fig.savefig(f"output/{file}")
