from typing import Callable, Tuple, List
import random
import numpy as np
import matplotlib.pyplot as plt

from models import Task


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
                 max_part_of_processors_number: float = 1,
                 print_plots=False):
        self.n = task_number
        self.processors_number = processors_number
        self.coefficient_of_variation = coefficient_of_variation
        self.load = max_load
        self._big_tasks = 0
        self._p_of_big, self._min_max_small, self._min_max_big = Generator.SETTINGS[self.coefficient_of_variation]
        self.max_part_of_processors_number = max_part_of_processors_number
        self.print_plots = print_plots
        self.length_function = lambda z, n: z.base_length / n

    def generate(self):
        print("===== Data generation =====")
        base_lengths = self._generate_base_length()

        print("Number of big tasks")
        print(self._big_tasks)

        print("\nAverage task length")
        print(np.mean(base_lengths))

        print("\nAverage task length divided by min processors")
        mean_run_time = np.mean([base_lengths[i] for i in range(self.n)])
        print(mean_run_time)

        print("\nAverage time to submit tasks")
        mean_time_space = mean_run_time / (self.load * self.processors_number)
        print(mean_time_space)

        print("\nAverage time to submit tasks")
        time_spaces = np.random.normal(mean_time_space, mean_time_space * 0.05, self.n)
        print(np.mean(time_spaces))

        time = []
        clock = 0
        for space in time_spaces:
            time.append(clock)
            clock += abs(space)

        if self.print_plots:
            self._print_plot(base_lengths, time_spaces)

        print("===== End of data generation =====")
        return [Task(i, time[i], 1, int(self.max_part_of_processors_number * self.processors_number),
                     base_lengths[i], self.length_function) for i in range(self.n)]

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

    def _print_plot(self, base_lengths, time_spaces):
        fig, axs = plt.subplots(nrows=2)
        fig.tight_layout()

        axs[0].hist(base_lengths, bins=max(10, self.n // 10))
        axs[0].set_title("Task duration distribution")

        axs[1].hist(time_spaces, bins=min(25, max(10, self.n // 25)))
        axs[1].set_title("Task submitting distribution")

        fig.savefig("output/distribution.png")
