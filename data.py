import csv
from collections import defaultdict
from enum import Enum
from typing import Optional, Any, List, Dict, DefaultDict, Tuple

from cost_functions import LengthFunctionType
from metrics import Metrics


class Variable(Enum):
    N_PROCESORS = "N"
    TASK_NUMBER = "M"
    MAX_LOAD = "$\\rho_{max}$"
    COV = "$V_s$"
    LENGTH_FUNCTION = "$p(n, s_i, n_{i,min}, n_{i,max})$"


class Parameters:
    def __init__(self, test_number: int, n_procesors: int, task_number: int, max_load: float, cov: float,
                 length_function: LengthFunctionType):
        self.test_number = test_number
        self.n_procesors = n_procesors
        self.task_number = task_number
        self.max_load = max_load
        self.cov = cov
        self.length_function = length_function

    def __hash__(self) -> int:
        return hash((self.test_number, self.n_procesors, self.task_number, self.max_load, self.cov,
                     self.length_function))

    def __eq__(self, other: 'Parameters') -> bool:
        return (self.test_number, self.n_procesors, self.task_number, self.max_load, self.cov,
                self.length_function) == \
               (other.test_number, other.n_procesors, other.task_number, other.max_load, other.cov,
                other.length_function)

    def make_copy_without_test_number(self) -> 'Parameters':
        return Parameters(0, self.n_procesors, self.task_number, self.max_load, self.cov,
                          self.length_function)

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
        elif testing_type == Variable.LENGTH_FUNCTION:
            params.length_function = val
        return params

    def print(self):
        print(f"n_procesors={self.n_procesors}, task_number={self.task_number}")
        print(f"max_load={self.max_load}, cov={self.cov}")
        print(f"length_function={self.length_function}")

    @staticmethod
    def list() -> List[str]:
        return ["test_number", "n_procesors",
                "task_number",
                "max_load", "cov",
                "length_function"]

    def to_dict(self) -> Dict[str, str]:
        return {"test_number": str(self.test_number), "n_procesors": str(self.n_procesors),
                "task_number": str(self.task_number),
                "max_load": str(self.max_load), "cov": str(self.cov),
                "length_function": str(self.length_function.name)}

    @staticmethod
    def from_dict(tup: Dict[str, str]) -> 'Parameters':
        return Parameters(int(tup["test_number"]), int(tup["n_procesors"]), int(tup["task_number"]),
                          float(tup["max_load"]), float(tup["cov"]), LengthFunctionType[tup["length_function"]])


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