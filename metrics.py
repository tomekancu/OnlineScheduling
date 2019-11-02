from typing import List, DefaultDict
from collections import defaultdict

from schedulers.models import Procesor
from task import Task


class Metrics:

    def __init__(self, max_end: float, sum_from_show_to_end: float, sum_from_show_to_end_minus_ideal: float):
        self.max_end = max_end
        self.sum_from_show_to_end = sum_from_show_to_end
        self.sum_from_show_to_end_minus_ideal = sum_from_show_to_end_minus_ideal

    def __str__(self):
        return f"Metric(max={round(self.max_end, 2)}, sum_end={round(self.sum_from_show_to_end, 2)}, " \
               f"sum_end_ideal={round(self.sum_from_show_to_end_minus_ideal, 2)})"


def _get_end_of_tasks(scheduling: List[Procesor]) -> DefaultDict[Task, float]:
    result = defaultdict(lambda: 0.0)
    for p in scheduling:
        for e in p.tasks:
            result[e.task] = max(result[e.task], e.end)
    return result


def get_max_end(scheduling: List[Procesor]) -> float:
    result = 0
    for p in scheduling:
        result = max(result, p.tasks[-1].end)
    return result


def get_sum_from_show_to_end(scheduling: List[Procesor]) -> float:
    task_end = _get_end_of_tasks(scheduling)
    result = sum(end - t.ready for t, end in task_end.items())
    return result


def get_sum_from_show_to_end_minus_ideal(scheduling: List[Procesor]) -> float:
    task_end = _get_end_of_tasks(scheduling)
    result = sum((end - t.ready - t.calc_length(len(scheduling))) for t, end in task_end.items())
    return result


def get_metrics(scheduling: List[Procesor]) -> Metrics:
    return Metrics(get_max_end(scheduling),
                   get_sum_from_show_to_end(scheduling),
                   get_sum_from_show_to_end_minus_ideal(scheduling))
