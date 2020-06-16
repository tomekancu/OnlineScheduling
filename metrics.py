from typing import Tuple, List, DefaultDict, Dict
from enum import Enum, auto
from collections import defaultdict
from statistics import mean

from models import Procesor, Task


class MetricType(Enum):
    MAX_END = auto()
    MEAN_RESPONSE_TIME = "$\\bar{t_f}$"
    MEAN_PROCESSING_TIME = "$\\bar{t_p}$"
    MEAN_DELAY_TIME = "$\\bar{t_o}$"
    MEAN_DELAY_PROCESSING_TIME = "$\\bar{t_o'}$"
    MEAN_IDEAL_DELAY_TIME = "$\\bar{t_o} + \\bar{t_o'}$"
    PROCESSING_TIME_TO_RESPONSE_TIME = auto()
    DELAY_TIME_TO_RESPONSE_TIME = "$\\varphi_o$"
    DELAY_PROCESSING_TIME_TO_RESPONSE_TIME = "$\\varphi_o'$"
    IDEAL_DELAY_TIME_TO_RESPONSE_TIME = "$\\varphi_o + \\varphi_o'$"
    RESOURCE_USAGE = "$\\varphi_r$"
    ACTUAL_RESOURCE_LOAD = "$\\rho$"


class Metrics:

    def __init__(self, max_end: float, mean_response_time: float, mean_processing_time: float,
                 mean_ideal_delay_time: float, resource_usage: float, actual_resource_load: float = -1):
        self.max_end = max_end
        self.mean_response_time = mean_response_time
        self.mean_processing_time = mean_processing_time
        self.mean_delay_time = self.mean_response_time - self.mean_processing_time
        self.mean_ideal_delay_time = mean_ideal_delay_time
        self.mean_delay_processing_time = self.mean_ideal_delay_time - self.mean_delay_time
        self.processing_time_to_response_time = self.mean_processing_time / self.mean_response_time
        self.delay_time_to_response_time = self.mean_delay_time / self.mean_response_time
        self.delay_processing_time_to_response_time = self.mean_delay_processing_time / self.mean_response_time
        self.ideal_delay_time_to_response_time = self.mean_ideal_delay_time / self.mean_response_time
        self.resource_usage = resource_usage
        self.actual_resource_load = actual_resource_load

    def __str__(self):
        return f"M(m={round(self.max_end, 2)}, m_r_t={round(self.mean_response_time, 2)}, " \
               f"m_p_t={round(self.mean_processing_time, 2)}, " \
               f"p_t_r_t={round(self.processing_time_to_response_time, 2)},\n" \
               f"m_d_t={round(self.mean_delay_time, 2)}, d_t_r_t={round(self.delay_time_to_response_time, 2)}, " \
               f"m_i_d_t={round(self.mean_ideal_delay_time, 2)}, " \
               f"m_d_p_t={round(self.mean_delay_processing_time, 2)}, " \
               f"i_t_r_t={round(self.ideal_delay_time_to_response_time, 2)}, " \
               f"r_u={round(self.resource_usage, 2)}, " \
               f"a_r_l={round(self.actual_resource_load, 2)})"

    def set_arl(self, max_end: float):
        self.actual_resource_load = self.resource_usage * self.max_end / max_end

    def get(self, typ: MetricType) -> float:
        if typ == MetricType.MAX_END:
            return self.max_end
        elif typ == MetricType.MEAN_RESPONSE_TIME:
            return self.mean_response_time
        elif typ == MetricType.MEAN_PROCESSING_TIME:
            return self.mean_processing_time
        elif typ == MetricType.MEAN_DELAY_TIME:
            return self.mean_delay_time
        elif typ == MetricType.MEAN_DELAY_PROCESSING_TIME:
            return self.mean_delay_processing_time
        elif typ == MetricType.MEAN_IDEAL_DELAY_TIME:
            return self.mean_ideal_delay_time
        elif typ == MetricType.PROCESSING_TIME_TO_RESPONSE_TIME:
            return self.processing_time_to_response_time
        elif typ == MetricType.DELAY_TIME_TO_RESPONSE_TIME:
            return self.delay_time_to_response_time
        elif typ == MetricType.DELAY_PROCESSING_TIME_TO_RESPONSE_TIME:
            return self.delay_processing_time_to_response_time
        elif typ == MetricType.IDEAL_DELAY_TIME_TO_RESPONSE_TIME:
            return self.ideal_delay_time_to_response_time
        elif typ == MetricType.RESOURCE_USAGE:
            return self.resource_usage
        elif typ == MetricType.ACTUAL_RESOURCE_LOAD:
            return self.actual_resource_load
        return 0

    @staticmethod
    def list() -> List[str]:
        return ["max_end",
                "mean_response_time",
                "mean_processing_time",
                "mean_ideal_delay_time",
                "resource_usage",
                "actual_resource_load"]

    def to_dict(self) -> Dict[str, str]:
        return {"max_end": str(self.max_end),
                "mean_response_time": str(self.mean_response_time),
                "mean_processing_time": str(self.mean_processing_time),
                "mean_ideal_delay_time": str(self.mean_ideal_delay_time),
                "resource_usage": str(self.resource_usage),
                "actual_resource_load": str(self.actual_resource_load)}

    @staticmethod
    def from_dict(tup: Dict[str, str]) -> 'Metrics':
        return Metrics(float(tup["max_end"]), float(tup["mean_response_time"]), float(tup["mean_processing_time"]),
                       float(tup["mean_ideal_delay_time"]), float(tup["resource_usage"]),
                       float(tup["actual_resource_load"]))


def get_max_end(scheduling: List[Procesor]) -> float:
    result = 0
    for p in scheduling:
        last_task = p.get_last_task()
        if last_task is not None:
            result = max(result, last_task.end)
    return result


def _get_end_of_tasks(scheduling: List[Procesor]) -> DefaultDict[Task, float]:
    result = defaultdict(lambda: 0.0)
    for p in scheduling:
        for e in p.tasks:
            result[e.task] = max(result[e.task], e.end)
    return result


def _get_response_time(scheduling: List[Procesor]) -> Dict[Task, float]:
    result = {}
    end_of_tasks = _get_end_of_tasks(scheduling)
    for t, end in end_of_tasks.items():
        result[t] = end - t.ready
    return result


def _get_mean_response_time(resposne_time: Dict[Task, float]) -> float:
    return mean(resposne_time.values())


def _join_ranges(parts: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    if len(parts) == 0:
        return []
    t = sorted(parts)
    stack = [t.pop(0)]
    for start, end in t:
        top_start, top_end = stack[-1]
        if top_end < start:
            stack.append((start, end))
        elif top_end < end:
            stack[-1] = (top_start, end)
    return stack


def _get_processing(scheduling: List[Procesor]) -> DefaultDict[Task, List[Tuple[float, float]]]:
    result = defaultdict(lambda: [])
    for procesor in scheduling:
        for part in procesor.tasks:
            result[part.task].append((part.start, part.end))
    for task in result:
        result[task] = _join_ranges(result[task])
    return result


def _get_processing_time(scheduling: List[Procesor]) -> Dict[Task, float]:
    result = {}
    processing = _get_processing(scheduling)
    for t, parts in processing.items():
        result[t] = sum(end - start for start, end in parts)
    return result


def _get_mean_processing_time(scheduling: List[Procesor]) -> float:
    processing_time = _get_processing_time(scheduling)
    return mean(processing_time.values())


def _get_mean_ideal_delay_time(resposne_time: Dict[Task, float], number_of_procesors: int) -> float:
    return mean((response - t.calc_length(number_of_procesors)) for t, response in resposne_time.items())


def _get_sum_of_procesor_time(scheduling: List[Procesor]) -> float:
    result = 0
    for proccesor in scheduling:
        result += sum(t.busy() for t in proccesor.tasks)
    return result


def _get_actual_resource_load(scheduling: List[Procesor], max_end: float) -> float:
    return _get_sum_of_procesor_time(scheduling) / (len(scheduling) * max_end)


def make_metrics(scheduling: List[Procesor]) -> Metrics:
    max_end = get_max_end(scheduling)
    resposne_time = _get_response_time(scheduling)
    mean_response_time = _get_mean_response_time(resposne_time)
    mean_processing_time = _get_mean_processing_time(scheduling)
    mean_ideal_delay_time = _get_mean_ideal_delay_time(resposne_time, len(scheduling))
    actual_resource_load = _get_actual_resource_load(scheduling, max_end)
    return Metrics(max_end,
                   mean_response_time,
                   mean_processing_time,
                   mean_ideal_delay_time,
                   actual_resource_load)


def make_mean_metrics(metrics: List[Metrics]) -> Metrics:
    n = len(metrics)
    max_end = sum(x.max_end for x in metrics) / n
    mean_response_time = sum(x.mean_response_time for x in metrics) / n
    mean_processing_time = sum(x.mean_processing_time for x in metrics) / n
    mean_ideal_delay_time = sum(x.mean_ideal_delay_time for x in metrics) / n
    actual_resource_load = sum(x.resource_usage for x in metrics) / n
    relative_resource_load = sum(x.actual_resource_load for x in metrics) / n
    return Metrics(max_end,
                   mean_response_time,
                   mean_processing_time,
                   mean_ideal_delay_time,
                   actual_resource_load,
                   relative_resource_load)
