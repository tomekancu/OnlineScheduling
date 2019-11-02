from typing import Callable, Tuple
import random
import numpy as np
import matplotlib.pyplot as plt

from models import Task


class Generator:

    def __init__(self, n: int,
                 min_max_resources: Tuple[int, int],
                 # bimodal distribution of base length of task
                 min_max_small: Tuple[int, int], min_max_big: Tuple[int, int], p_of_big: float,
                 length_function: Callable[['Task', int], float],
                 std_function=np.sqrt, print_plots=False):
        self.n = n
        self.min_max_resources = min_max_resources
        self.min_max_small = min_max_small
        self.min_max_big = min_max_big
        self.p_of_big = p_of_big
        self.std_function = std_function
        self.length_function = length_function
        self.print_plots = print_plots

    def generate(self):
        base_lengths = [int(self._bimodal()) for _ in range(self.n)]
        mean = np.mean(base_lengths)

        time_spaces = np.random.normal(mean, self.std_function(mean), self.n)
        time = []
        clock = 0
        for space in time_spaces:
            time.append(clock)
            clock += space

        if self.print_plots:
            self._print_plot(base_lengths, time_spaces)

        min_resources, max_resources = self.min_max_resources
        return [Task(i, time[i], min_resources, max_resources,
                     base_lengths[i], self.length_function) for i in range(self.n)]

    def _bimodal(self):
        toss = np.random.choice((1, 2), p=(1 - self.p_of_big, self.p_of_big))
        if toss == 1:
            low1, high1 = self.min_max_small
            return random.triangular(low1, high1)
        else:
            low2, high2 = self.min_max_big
            return random.triangular(low2, high2)

    def _print_plot(self, base_lengths, time_spaces):
        plt.subplot(2, 1, 1)
        plt.hist(base_lengths, bins=max(10, self.n // 10))
        plt.title("Task duration distribution")

        plt.subplot(2, 1, 2)
        plt.hist(time_spaces, bins=min(25, max(10, self.n // 25)))
        plt.title("Task submitting distribution")

        plt.tight_layout()
        plt.savefig("output/distribution.png")
