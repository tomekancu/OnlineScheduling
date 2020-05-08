from typing import Tuple, List
import random
import numpy as np
import matplotlib.pyplot as plt

from models import Task
from cost_functions import LengthFunctionType


class Generator:
    SETTINGS = {
        0.3: (0.5, (1000, 1200), (1950, 2150)),
        1: (0.35, (1000, 2000), (17000, 18000)),
        2: (0.15, (1000, 2000), (57000, 58000)),
        5: (0.03, (1000, 1500), (401500, 402000)),
        10: (0.008, (1000, 2000), (2202000, 2203000))
    }

    def __init__(self, task_number: int,
                 processors_number: int,
                 coefficient_of_variation: float,
                 max_load: float,
                 length_function: LengthFunctionType = LengthFunctionType.CONCAVE,
                 print_plots=False):
        self.n = task_number
        self.processors_number = processors_number
        self.coefficient_of_variation = coefficient_of_variation
        self.max_load = max_load
        self._big_tasks = 0
        self._p_of_big, self._min_max_small, self._min_max_big = Generator.SETTINGS[self.coefficient_of_variation]
        self.print_plots = print_plots
        self.length_function = length_function

    def generate(self):
        mins = [int(random.randint(1, max(int(0.05 * self.processors_number), 1)))
                for i in range(self.n)]
        maxes = [int(random.randint(max(int(0.5 * self.processors_number), mins[i]), self.processors_number))
                 for i in range(self.n)]

        base_lengths = self._generate_base_length()

        mean_max_run_time = self._get_mean_max_run_time(base_lengths, mins, maxes)
        mean_time_space = mean_max_run_time / (self.max_load * self.processors_number)
        time_spaces = np.random.exponential(mean_time_space, self.n)

        time = []
        clock = 0
        for space in time_spaces:
            time.append(clock)
            clock += abs(space)

        if self.print_plots:
            self._print_plot(base_lengths, time_spaces, mins, maxes)

        return [Task(i, time[i], mins[i], maxes[i], base_lengths[i], self.length_function.get_function())
                for i in range(self.n)]

    def _get_mean_max_run_time(self, base_lengths, mins, maxes):
        function = self.length_function.get_function()
        if self.length_function == LengthFunctionType.CONCAVE_FLAT:
            return np.mean([function(Task(0, 0, n_min, n_max, base, function), n_max) * n_max
                            for base, n_min, n_max in zip(base_lengths, mins, maxes)])
        return np.mean([function(Task(0, 0, n_min, n_max, base, function), n_min) * n_min
                        for base, n_min, n_max in zip(base_lengths, mins, maxes)])

    def get_mid_task_size(self) -> float:
        return (self._min_max_big[0] - self._min_max_small[1]) / 2

    def _generate_base_length(self):
        base_lengths = self._bimodal()
        coef = self._coefficient_of_variation(base_lengths)
        direction = 1
        min_s, max_s = self._min_max_small
        step = max_s - min_s

        while abs(self.coefficient_of_variation - coef) > self.coefficient_of_variation * 0.1:
            self._big_tasks = 0
            min_b, max_b = self._min_max_big
            self._min_max_big = (min_b + step * direction, max_b + step * direction)
            base_lengths = self._bimodal()
            coef = self._coefficient_of_variation(base_lengths)
            if coef > self.coefficient_of_variation:
                direction = -1
                step = step / 2 if step / 2 > 0 else 1
            else:
                direction = 1
                step = step * 2.1

        return base_lengths

    def _bimodal(self):
        bimodal, self._big_tasks = Generator.bimodal_n(self.n, self._min_max_small, self._min_max_big, self._p_of_big)
        return bimodal

    @staticmethod
    def bimodal_n(n, min_max_small, min_max_big, p_of_big) -> Tuple[List[float], int]:
        bimodals, bigs = map(list, zip(*(Generator.bimodal1(min_max_small, min_max_big, p_of_big) for _ in range(n))))
        return bimodals, sum(bigs)

    @staticmethod
    def bimodal1(min_max_small, min_max_big, p_of_big) -> Tuple[float, bool]:
        toss = np.random.choice((1, 2), p=(1 - p_of_big, p_of_big))
        if toss == 1:
            low1, high1 = min_max_small
            return random.triangular(low1, high1), False
        else:
            low2, high2 = min_max_big
            return random.triangular(low2, high2), True

    @staticmethod
    def _coefficient_of_variation(data: list):
        mean_p = np.mean(data)
        std_p = np.std(data)
        return std_p / mean_p

    def _print_plot(self, base_lengths, time_spaces, mins, maxs):
        fig, axs = plt.subplots(nrows=4)
        fig.tight_layout()

        axs[0].hist(base_lengths, bins=max(10, self.n // 10))
        axs[0].set_title("Task duration distribution")

        axs[1].hist(time_spaces, bins=min(25, max(10, self.n // 25)))
        axs[1].set_title("Task submitting distribution")

        axs[2].hist(mins, bins=max(1, int(0.05 * self.processors_number)))
        axs[2].set_title("Mins resources distribution")

        axs[3].hist(maxs, bins=max(1, int(0.5 * self.processors_number)) + 1)
        axs[3].set_title("Maxs resources distribution")

        fig.savefig("output/distribution.png")
