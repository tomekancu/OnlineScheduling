from collections import defaultdict
from enum import Enum, auto
from typing import Any, List, Dict, Tuple

from cost_functions import LengthFunctionType
from generator import Generator
from metrics import make_metrics, Metrics, make_mean_metrics
from plot import print_metrics
from schedulers.abstract import AbstractScheduler, comparator_oldest_task, comparator_smallest_task
from schedulers.naive import NaiveScheduler
from schedulers.preemption import PreemptionScheduler
from schedulers.separate import SeparateScheduler
from schedulers.separate_with_premption import SeparateWithPremptionScheduler

ALL_COV = [0.3, 1, 2, 5, 10]


class Variable(Enum):
    TASK_NUMBER = auto()
    N_PROCESORS = auto()
    COV = auto()
    MAX_LOAD = auto()
    MAX_PART_OF_PROCESOR_NUMBER = auto()
    LENGTH_FUNCTION = auto()


class Parameters:
    def __init__(self, test_number: int, n_procesors: int, task_number: int, max_load: float, cov: float,
                 max_part_of_processors: float, length_function: LengthFunctionType):
        self.test_number = test_number
        self.n_procesors = n_procesors
        self.task_number = task_number
        self.max_load = max_load
        self.cov = cov
        self.max_part_of_processors = max_part_of_processors
        self.length_function = length_function

    def __hash__(self) -> int:
        return hash((self.test_number, self.n_procesors, self.task_number, self.max_load, self.cov,
                     self.max_part_of_processors, self.length_function))

    def __eq__(self, other: 'Parameters') -> bool:
        return (self.test_number, self.n_procesors, self.task_number, self.max_load, self.cov,
                self.max_part_of_processors, self.length_function) == \
               (other.test_number, other.n_procesors, other.task_number, other.max_load, other.cov,
                other.max_part_of_processors, other.length_function)

    def update(self, testing_type: Variable, val: Any) -> 'Parameters':
        params = Parameters(self.test_number, self.n_procesors, self.task_number, self.max_load, self.cov,
                            self.max_part_of_processors, self.length_function)
        if testing_type == Variable.N_PROCESORS:
            params.n_procesors = val
        elif testing_type == Variable.TASK_NUMBER:
            params.task_number = val
        elif testing_type == Variable.MAX_LOAD:
            params.max_load = val
        elif testing_type == Variable.COV:
            params.cov = val
        elif testing_type == Variable.MAX_PART_OF_PROCESOR_NUMBER:
            params.max_part_of_processors = val
        elif testing_type == Variable.LENGTH_FUNCTION:
            params.length_function = val
        return params

    def print(self):
        print(f"n_procesors={self.n_procesors}, task_number={self.task_number}")
        print(f"max_load={self.max_load}, cov={self.cov}")
        print(f"max_part_of_processors={self.max_part_of_processors}, length_function={self.length_function}")


def to_plot(metrics: Dict[Tuple[Parameters, str], List[Metrics]],
            default: Parameters, testing_type: Variable, testing_values: List[Any]) -> Dict[Any, Dict[str, Metrics]]:
    result = {}
    for val in testing_values:
        params = default.update(testing_type, val)
        alg = {}
        for (p, n), l in filter(lambda x: x[0][0] == params, metrics.items()):
            alg[n] = make_mean_metrics(l)
        result[val] = alg
    return result


def make_research(default: Parameters, testing_type: Variable, testing_values: List[Any],
                  schedulers: List[AbstractScheduler]):
    default.print()
    print(f"testing_type={testing_type}, testing_values={testing_values}")
    metrics_all = defaultdict(lambda: [])
    for val in testing_values:
        print(f"testing: {val}")
        params = default.update(testing_type, val)
        gen = Generator(task_number=params.task_number, processors_number=params.n_procesors,
                        coefficient_of_variation=params.cov, max_load=params.max_load,
                        length_function=params.length_function.get_function(),
                        max_part_of_processors_number=params.max_part_of_processors,
                        print_plots=False)
        instance = gen.generate()

        for i, scheduler in enumerate(schedulers):
            if isinstance(scheduler, SeparateScheduler) or isinstance(scheduler, SeparateWithPremptionScheduler):
                scheduler.task_size_treshold = gen.get_mid_task_size()
            print(i, scheduler.get_name())
            scheduler.schedule(params.n_procesors, instance)
            metrics_all[(params, scheduler.get_name())].append(make_metrics(scheduler.procesors))
    gather = to_plot(
        metrics_all,
        default, testing_type, testing_values
    )
    print_metrics(gather,
                  f"metrics max_load{default.max_load} cov{default.cov} max_part_of_processors{default.max_part_of_processors} "
                  f"length_function{default.length_function} {testing_type}",
                  f"metrics-max-load-{default.max_load}-cov-{default.cov}-max_part_of_processors-{default.max_part_of_processors}"
                  f"-length_function-{default.length_function}-{testing_type}.png")


def research():
    make_research(Parameters(
        test_number=1,
        n_procesors=100,
        task_number=10_000,
        max_load=0.2,
        cov=0.3,
        max_part_of_processors=1.0,
        length_function=LengthFunctionType.CONCAVE
    ), Variable.COV, ALL_COV,
        [
            NaiveScheduler(),
            SeparateScheduler(0, 0.25),
            SeparateWithPremptionScheduler(0, 0.25),
            SeparateWithPremptionScheduler(0, 0.5),
            PreemptionScheduler(),
        ])
