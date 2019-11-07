from typing import List, DefaultDict
from collections import defaultdict

from models import Procesor, Task


class Metrics:

    def __init__(self, max_end: float, sum_of_procesor_busy: float, busy_fraction: float, sum_of_ideal_delay: float):
        self.max_end = max_end
        self.sum_of_procesor_busy = sum_of_procesor_busy
        self.busy_fraction = busy_fraction
        self.sum_of_ideal_delay = sum_of_ideal_delay

    def __str__(self):
        return f"M(m={round(self.max_end, 2)}, s_busy={round(self.sum_of_procesor_busy, 2)}, " \
               f"f_busy={round(self.busy_fraction, 2)}, s_ideal_delay={round(self.sum_of_ideal_delay, 2)})"


def _get_end_of_tasks(scheduling: List[Procesor]) -> DefaultDict[Task, float]:
    result = defaultdict(lambda: 0.0)
    for p in scheduling:
        for e in p.tasks:
            result[e.task] = max(result[e.task], e.end)
    return result


def get_max_end(scheduling: List[Procesor]) -> float:
    result = 0
    for p in scheduling:
        last_task = p.get_last_task()
        if last_task is not None:
            result = max(result, last_task.end)
    return result


def get_sum_of_procesor_busy(scheduling: List[Procesor]) -> float:
    result = 0
    for proccesor in scheduling:
        result += sum(t.busy() for t in proccesor.tasks)
    return result


def get_busy_fraction(scheduling: List[Procesor]) -> float:
    return get_sum_of_procesor_busy(scheduling) / (len(scheduling) * get_max_end(scheduling))


def get_sum_of_ideal_delay(scheduling: List[Procesor]) -> float:
    task_end = _get_end_of_tasks(scheduling)
    result = sum((end - t.ready - t.calc_length(len(scheduling))) for t, end in task_end.items())
    return result


def get_metrics(scheduling: List[Procesor]) -> Metrics:
    return Metrics(get_max_end(scheduling),
                   get_sum_of_procesor_busy(scheduling),
                   get_busy_fraction(scheduling),
                   get_sum_of_ideal_delay(scheduling))
