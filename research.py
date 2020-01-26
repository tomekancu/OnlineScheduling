from collections import defaultdict
from enum import Enum, auto
from typing import Any, List, Dict, Tuple

from cost_functions import LengthFunctionType
from generator import Generator
from metrics import make_metrics, Metrics, make_mean_metrics
from plot import print_metrics
from schedulers.naive import NaiveScheduler
from schedulers.preemption import PreemptionScheduler
from schedulers.separate import SeparateScheduler
from schedulers.separate_with_premption import SeparateWithPremptionScheduler


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
            default: Parameters, testing_type: Variable, testing_values: List[Any]) -> Dict[float, Dict[str, Metrics]]:
    result = {}
    for val in testing_values:
        params = default.update(testing_type, val)
        alg = {}
        for (p, n), l in filter(lambda x: x[0][0] == params, metrics.items()):
            alg[n] = make_mean_metrics(l)
        result[val] = alg
    return result


def make_research(default: Parameters, testing_type: Variable, testing_values: List[Any]):
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

        print("first")
        scheduler1 = NaiveScheduler()
        scheduler1.schedule(params.n_procesors, instance)
        metrics_all[(params, scheduler1.get_name())].append(make_metrics(scheduler1.procesors))

        print("second25")
        scheduler2 = SeparateScheduler(gen.get_mid_task_size(), 0.25)
        scheduler2.schedule(params.n_procesors, instance)
        metrics_all[(params, scheduler2.get_name())].append(make_metrics(scheduler2.procesors))

        # print("second50")
        # scheduler3 = SeparateScheduler(gen.get_mid_task_size(), 0.50)
        # scheduler3.schedule(n_procesors, instance)
        # metr[scheduler3.get_name()] = make_metrics(scheduler3.procesors)

        print("second25v2")
        scheduler4 = SeparateWithPremptionScheduler(gen.get_mid_task_size(), 0.25)
        scheduler4.schedule(params.n_procesors, instance)
        metrics_all[(params, scheduler4.get_name())].append(make_metrics(scheduler4.procesors))

        print("second50v2")
        scheduler5 = SeparateWithPremptionScheduler(gen.get_mid_task_size(), 0.5)
        scheduler5.schedule(params.n_procesors, instance)
        metrics_all[(params, scheduler5.get_name())].append(make_metrics(scheduler5.procesors))
        print("third")

        scheduler6 = PreemptionScheduler()
        scheduler6.schedule(params.n_procesors, instance)
        metrics_all[(params, scheduler6.get_name())].append(make_metrics(scheduler6.procesors))
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
    ), Variable.COV, [0.3, 1, 2, 5, 10])
