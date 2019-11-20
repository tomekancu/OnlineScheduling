from typing import Callable, Tuple
import random
import numpy as np
import matplotlib.pyplot as plt

from models import Task


class Generator:

    SETTINGS = {
        0.3: {'p': 0.5},
        1: {'p': 0.4},
        2: {'p': 0.15},
        5: {'p': 0.03},
        10: {'p': 0.005}
    }

    def __init__(self, task_number: int,
                 processors_number: int,
                 parameter,
                 load: float,
                 print_plots=False):
        self.n = task_number
        self.param = parameter
        self.proc = processors_number
        self.load = load
        self._big_tasks = 0
        self._min_max_small = (100, 350)
        self._min_max_big = self._min_max_small
        self._p_of_big = Generator.SETTINGS[self.param]['p']
        self.length_function = lambda z, n: z.base_length / n
        self.print_plots = print_plots

    def generate(self):
        print("===== Data generation =====")
        base_lengths = self._generate_base_length()
        min_r, max_r = self._calculate_min_max()

        print("Number of big tasks")
        print(self._big_tasks)

        print("\nAverage task length")
        print(np.mean(base_lengths))

        print("\nAverage task length divided by min processors")
        mean_run_time = np.mean([base_lengths[i] / min_r[i] for i in range(self.n)])
        print(mean_run_time)

        print("\nAverage time to submit tasks")
        mean_time_space = mean_run_time / (self.load * self.proc)
        print(mean_time_space)

        print("\nAverage time to submit tasks")
        time_spaces = np.random.normal(mean_time_space, mean_time_space * 0.05, self.n)
        print(np.mean(time_spaces))

        time = []
        clock = 0
        for space in time_spaces:
            time.append(clock)
            clock += int(abs(space))

        if self.print_plots:
            self._print_plot(base_lengths, time_spaces)

        print("===== End of data generation =====")
        return [Task(i, time[i], min_r[i], max_r[i],
                     base_lengths[i], self.length_function) for i in range(self.n)]

    def _generate_base_length(self):
        base_lengths = [int(self._bimodal()) for _ in range(self.n)]
        coef = self._coefficient_of_variation(base_lengths)
        direction = 1
        min_s, max_s = self._min_max_small
        step = max_s - min_s

        while not (self.param - self.param * 0.05 < coef < self.param + self.param * 0.05):
            self._big_tasks = 0
            min_b, max_b = self._min_max_big
            self._min_max_big = (min_b + step * direction, max_b + step * direction)
            base_lengths = [int(self._bimodal()) for _ in range(self.n)]
            coef = self._coefficient_of_variation(base_lengths)
            if coef > self.param:
                direction = -1
                step = step // 2 if step // 2 > 0 else 1
            else:
                direction = 1
                step = int(step * 2.1)

        return base_lengths

    def _bimodal(self):
        toss = np.random.choice((1, 2), p=(1 - self._p_of_big, self._p_of_big))
        if toss == 1:
            low1, high1 = self._min_max_small
            return random.triangular(low1, high1)
        else:
            self._big_tasks += 1
            low2, high2 = self._min_max_big
            return random.triangular(low2, high2)

    def _calculate_min_max(self):
        min_r = np.random.gamma(2., 1., self.n)
        min_r = [int(1 + np.round(i)) for i in min_r]
        max_r = np.random.gamma(1., 1., self.n)
        max_r = [int(self.proc / 2 + i * (self.proc / 2)) for i in max_r]
        # count, bins, ignored = plt.hist(max_r, 50, density=True)
        # y = bins ** (shape - 1) * (np.exp(-bins / scale) / (sps.gamma(shape) * scale ** shape))
        # plt.plot(bins, y, linewidth=2, color='r')
        # plt.show()
        min_max = [(i, j) if i < j else (i, j + i) for i, j in list(zip(min_r, max_r))]
        min_r, max_r = zip(*min_max)

        return min_r, max_r

    @staticmethod
    def _coefficient_of_variation(data: list):
        mean_p = np.mean(data)
        std_p = np.std(data)
        return std_p / mean_p

    def _print_plot(self, base_lengths, time_spaces):
        plt.subplot(2, 1, 1)
        plt.hist(base_lengths, bins=max(10, self.n // 10))
        plt.title("Task duration distribution")

        plt.subplot(2, 1, 2)
        plt.hist(time_spaces, bins=min(25, max(10, self.n // 25)))
        plt.title("Task submitting distribution")

        plt.tight_layout()
        plt.savefig("output/distribution.png")
