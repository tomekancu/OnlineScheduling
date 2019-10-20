from typing import Callable
import matplotlib.pyplot as plt


def print_scheduling(scheduling):
    colors = ['orange', 'blue', 'red', 'yellow', 'green', 'purple', 'pink', 'gray']
    fig, gnt = plt.subplots()
    gnt.grid(True)
    gnt.set_ylabel('Processor')

    gnt.set_yticks([15 + 10 * i for i in range(len(scheduling))])
    gnt.set_yticklabels([i for i in reversed(range(len(scheduling)))])

    for i, proc in enumerate(reversed(scheduling)):
        for j, tj in enumerate(proc):
            start, end, t_id = tj
            color = colors[t_id % len(colors)]
            gnt.broken_barh([(start, end-start)], (10.5 + 10 * i, 9), facecolors=color)

    plt.savefig("output/gantt.png")
