import random
from typing import Callable

import numpy as np
import matplotlib.pyplot as plt

from task import Task


class Generator:

    def __init__(self, N: int, low1: int, high1: int, low2: int, high2: int,
                 p: float, length_function: Callable[['Task', int], int], std_function=np.sqrt, save_plots=False):
        self.n = N
        self.low1 = low1
        self.high1 = high1
        self.low2 = low2
        self.high2 = high2
        self.p = p
        self.std_function = std_function
        self.length_function = length_function
        self.save_plots = save_plots

    def _bimodal(self):
        toss = np.random.choice((1, 2), p=(1-self.p, self.p))
        if toss == 1:
            return random.triangular(self.low1, self.high1)
        else:
            return random.triangular(self.low2, self.high2)

    def generate(self):
        nums = [int(self._bimodal()) for _ in range(self.n)]
        mean = np.mean(nums)

        time = [int(np.round(np.random.normal(mean, self.std_function(mean)))) for _ in range(self.n)]

        if self.save_plots:
            plt.subplot(2, 1, 1)
            plt.hist(nums, bins=max(10, self.n//10))
            plt.title("Task duration distribution")

            plt.subplot(2, 1, 2)
            plt.hist(time, bins=min(25, max(10, self.n//25)))
            plt.title("Task submitting distribution")
            plt.tight_layout()
            plt.savefig("img.png")

        return [Task(i, time[i], 0, 10, nums[i], self.length_function) for i in range(self.n)]




