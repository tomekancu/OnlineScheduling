import csv
from collections import defaultdict
from enum import Enum, auto
from typing import Any, List, Dict, DefaultDict, Tuple, Optional

from cost_functions import LengthFunctionType
from generator import Generator
from metrics import make_metrics, Metrics, make_mean_metrics
from plot import print_metrics
from schedulers.abstract import AbstractScheduler, comparator_smallest_task, comparator_oldest_task
from schedulers.abstract_separate import AbstractSeparateScheduler
from schedulers.naive import NaiveScheduler
from schedulers.preemption import PreemptionScheduler
from schedulers.separate import SeparateScheduler
from schedulers.separate_with_premption import SeparateWithPremptionScheduler


class Variable(Enum):
    N_PROCESORS = auto()
    TASK_NUMBER = auto()
    MAX_LOAD = auto()
    COV = auto()
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

    def make_copy_without_test_number(self) -> 'Parameters':
        return Parameters(0, self.n_procesors, self.task_number, self.max_load, self.cov,
                          self.max_part_of_processors, self.length_function)

    def make_instance_for(self, testing_type: Optional[Variable], val: Any) -> 'Parameters':
        params = self.make_copy_without_test_number()
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

    @staticmethod
    def list() -> List[str]:
        return ["test_number", "n_procesors",
                "task_number",
                "max_load", "cov",
                "max_part_of_processors",
                "length_function"]

    def to_dict(self) -> Dict[str, str]:
        return {"test_number": str(self.test_number), "n_procesors": str(self.n_procesors),
                "task_number": str(self.task_number),
                "max_load": str(self.max_load), "cov": str(self.cov),
                "max_part_of_processors": str(self.max_part_of_processors),
                "length_function": str(self.length_function)}

    @staticmethod
    def from_dict(tup: Dict[str, str]) -> 'Parameters':
        length_function = next(filter(lambda x: str(x) == tup["length_function"], LengthFunctionType))
        return Parameters(int(tup["test_number"]), int(tup["n_procesors"]), int(tup["task_number"]),
                          float(tup["max_load"]), float(tup["cov"]), float(tup["max_part_of_processors"]),
                          length_function)


class MetricsDatabase:
    def __init__(self, database_path: str = "output/metrics.csv"):
        self.database_path = database_path
        self.database: DefaultDict[Tuple[Parameters, str], List[Metrics]] = defaultdict(lambda: [])

    def load(self):
        self.database = defaultdict(lambda: [])
        try:
            with open(self.database_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';')
                for row in reader:
                    params = Parameters.from_dict(row)
                    metric = Metrics.from_dict(row)
                    name = row["name"]
                    self.save_metric(params, name, metric)
        except FileNotFoundError:
            print("No database")

    def save(self):
        with open(self.database_path, 'w', encoding='utf-8', newline='') as csvfile:
            fieldnames = ["name"] + Parameters.list() + Metrics.list()
            writer = csv.DictWriter(csvfile, fieldnames, delimiter=';')
            writer.writeheader()
            for (param, name), metrics in self.database.items():
                for metric in metrics:
                    to_write = {"name": name}
                    to_write.update(param.to_dict())
                    to_write.update(metric.to_dict())
                    writer.writerow(to_write)

    def get_metrics(self, params: Parameters, algorithm: str) -> List[Metrics]:
        return self.database.get((params.make_copy_without_test_number(), algorithm), list())

    def save_metric(self, params: Parameters, algorithm: str, metric: Metrics):
        return self.database[(params.make_copy_without_test_number(), algorithm)].append(metric)


def to_plot(metrics_database: MetricsDatabase,
            default: Parameters, testing_type: Variable, testing_values: List[Any],
            schedulers: List[AbstractScheduler]) -> Dict[Any, Dict[str, Metrics]]:
    result = {}
    for val in testing_values:
        params = default.make_instance_for(testing_type, val)
        alg = {}
        for scheduler in schedulers:
            alg_name = scheduler.get_name()
            alg_title = scheduler.get_title()
            metrics_list = metrics_database.get_metrics(params, alg_name)
            alg[alg_title] = make_mean_metrics(metrics_list)
        result[val] = alg
    return result


def make_research(default: Parameters, testing_type: Variable, testing_values: List[Any],
                  schedulers: List[AbstractScheduler]):
    default.print()
    print(f"testing_type={testing_type}, testing_values={testing_values}")
    metrics_database = MetricsDatabase()
    metrics_database.load()
    for test_id in range(default.test_number):
        print(f"test: {test_id}")
        for val in testing_values:
            print(f"test: {test_id} testing: {val}")
            params = default.make_instance_for(testing_type, val)
            gen = Generator(task_number=params.task_number, processors_number=params.n_procesors,
                            coefficient_of_variation=params.cov, max_load=params.max_load,
                            length_function=params.length_function.get_function(),
                            max_part_of_processors_number=params.max_part_of_processors,
                            print_plots=False)
            instance = gen.generate()

            for i, scheduler in enumerate(schedulers):
                if isinstance(scheduler, AbstractSeparateScheduler):
                    scheduler.task_size_treshold = gen.get_mid_task_size()
                name = scheduler.get_name()
                print(f"test: {test_id} testing: {val} i: {i+1}/{len(schedulers)} alg: {name}")
                in_database = metrics_database.get_metrics(params, name)
                if len(in_database) < default.test_number:
                    scheduler.schedule(params.n_procesors, instance)
                    metrics = make_metrics(scheduler.procesors)
                    metrics_database.save_metric(params, name, metrics)
            metrics_database.save()
    gather = to_plot(metrics_database, default, testing_type, testing_values, schedulers)
    print_metrics(gather,
                  f"metrics max_load{default.max_load} cov{default.cov} max_part_of_processors{default.max_part_of_processors} "
                  f"length_function{default.length_function} {testing_type}",
                  file=f"metrics-max-load-{default.max_load}-cov-{default.cov}"
                       f"-max_part_of_processors-{default.max_part_of_processors}"
                       f"-length_function-{default.length_function}-{testing_type}.png")


ALL_COV = [0.3, 1, 2, 5, 10]
ALL_PERCENT = [0.2, 0.4, 0.6, 0.8, 1.0]


def research():
    # test()
    schedulers = [
        NaiveScheduler(comparator_smallest_task),  # better
        NaiveScheduler(comparator_oldest_task),
        SeparateScheduler(0, 0.05, comparator_smallest_task),
        SeparateScheduler(0, 0.25, comparator_smallest_task),  # better
        SeparateScheduler(0, 0.5, comparator_smallest_task),
        SeparateScheduler(0, 0.75, comparator_smallest_task),
        SeparateScheduler(0, 0.95, comparator_smallest_task),
        SeparateScheduler(0, 0.05, comparator_oldest_task),
        SeparateScheduler(0, 0.25, comparator_oldest_task),
        SeparateScheduler(0, 0.5, comparator_oldest_task),
        SeparateScheduler(0, 0.75, comparator_oldest_task),
        SeparateScheduler(0, 0.95, comparator_oldest_task),
        SeparateWithPremptionScheduler(0, 0.05, comparator_smallest_task),
        SeparateWithPremptionScheduler(0, 0.25, comparator_smallest_task),
        SeparateWithPremptionScheduler(0, 0.5, comparator_smallest_task),
        SeparateWithPremptionScheduler(0, 0.75, comparator_smallest_task),
        SeparateWithPremptionScheduler(0, 0.95, comparator_smallest_task),
        SeparateWithPremptionScheduler(0, 0.05, comparator_oldest_task),
        SeparateWithPremptionScheduler(0, 0.25, comparator_oldest_task),
        SeparateWithPremptionScheduler(0, 0.5, comparator_oldest_task),
        SeparateWithPremptionScheduler(0, 0.75, comparator_oldest_task),
        SeparateWithPremptionScheduler(0, 0.95, comparator_oldest_task),  # better
        PreemptionScheduler(comparator_smallest_task),
        PreemptionScheduler(comparator_oldest_task),  # better
    ]
    parameters = Parameters(test_number=3, n_procesors=100, task_number=10_000, max_load=1.0, cov=10,
                            max_part_of_processors=1.0, length_function=LengthFunctionType.CONCAVE_FLAT)
    make_research(parameters, Variable.COV, ALL_COV, schedulers)
    parameters = Parameters(test_number=3, n_procesors=100, task_number=10_000, max_load=0.2, cov=10,
                            max_part_of_processors=1.0, length_function=LengthFunctionType.CONCAVE_FLAT)
    make_research(parameters, Variable.COV, ALL_COV, schedulers)
    parameters = Parameters(test_number=3, n_procesors=100, task_number=10_000, max_load=0.2, cov=0.3,
                            max_part_of_processors=1.0, length_function=LengthFunctionType.CONCAVE_FLAT)
    make_research(parameters, Variable.MAX_LOAD, ALL_PERCENT, schedulers)
    parameters = Parameters(test_number=3, n_procesors=100, task_number=10_000, max_load=0.2, cov=10,
                            max_part_of_processors=1.0, length_function=LengthFunctionType.CONCAVE)
    make_research(parameters, Variable.MAX_LOAD, ALL_PERCENT, schedulers)
