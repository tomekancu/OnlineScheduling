from enum import Enum, auto
from typing import Dict, Any, Tuple, List

from cost_functions import LengthFunctionType
from generator import Generator
from metrics import get_metrics
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


def make_research(default: Dict[Variable, Any], testing: Tuple[Variable, List[Any]]):
    n_procesors = default.get(Variable.N_PROCESORS, 100)
    task_number = default.get(Variable.TASK_NUMBER, 10_000)
    max_load = default.get(Variable.MAX_LOAD, 0.2)
    cov = default.get(Variable.COV, 0.3)
    max_part_of_processors = default.get(Variable.MAX_PART_OF_PROCESOR_NUMBER, 1.0)
    length_function = default.get(Variable.LENGTH_FUNCTION, LengthFunctionType.CONCAVE)
    testing_type, testing_values = testing

    metrics_all = {}
    print(f"n_procesors={n_procesors}, task_number={task_number}")
    print(f"max_load={max_load}, cov={cov}")
    print(f"max_part_of_processors={max_part_of_processors}, length_function={length_function}")
    print(f"testing_type={testing_type}, testing_values={testing_values}")
    for vals in testing_values:
        print(f"testing: {vals}")
        if testing_type == Variable.N_PROCESORS:
            n_procesors = vals
        elif testing_type == Variable.TASK_NUMBER:
            task_number = vals
        elif testing_type == Variable.MAX_LOAD:
            max_load = vals
        elif testing_type == Variable.COV:
            cov = vals
        elif testing_type == Variable.MAX_PART_OF_PROCESOR_NUMBER:
            max_part_of_processors = vals
        elif testing_type == Variable.LENGTH_FUNCTION:
            length_function = vals

        gen = Generator(task_number=task_number, processors_number=n_procesors,
                        coefficient_of_variation=cov, max_load=max_load,
                        length_function=length_function.get_function(),
                        max_part_of_processors_number=max_part_of_processors,
                        print_plots=False)
        instance = gen.generate()
        metr = {}

        print("first")
        scheduler1 = NaiveScheduler()
        scheduler1.schedule(n_procesors, instance)
        metr[scheduler1.get_name()] = get_metrics(scheduler1.procesors)

        print("second25")
        scheduler2 = SeparateScheduler(gen.get_mid_task_size(), 0.25)
        scheduler2.schedule(n_procesors, instance)
        metr[scheduler2.get_name()] = get_metrics(scheduler2.procesors)

        # print("second50")
        # scheduler3 = SeparateScheduler(gen.get_mid_task_size(), 0.50)
        # scheduler3.schedule(n_procesors, instance)
        # metr[scheduler3.get_name()] = get_metrics(scheduler3.procesors)

        print("second25v2")
        scheduler4 = SeparateWithPremptionScheduler(gen.get_mid_task_size(), 0.25)
        scheduler4.schedule(n_procesors, instance)
        metr[scheduler4.get_name()] = get_metrics(scheduler4.procesors)

        print("second50v2")
        scheduler5 = SeparateWithPremptionScheduler(gen.get_mid_task_size(), 0.5)
        scheduler5.schedule(n_procesors, instance)
        metr[scheduler5.get_name()] = get_metrics(scheduler5.procesors)

        print("third")
        scheduler6 = PreemptionScheduler()
        scheduler6.schedule(n_procesors, instance)
        metr[scheduler6.get_name()] = get_metrics(scheduler6.procesors)

        metrics_all[cov] = metr
    print_metrics(metrics_all,
                  f"metrics max_load{max_load} cov{cov} max_part_of_processors{max_part_of_processors} "
                  f"length_function{length_function} {testing_type}",
                  f"metrics-max-load-{max_load}-cov-{cov}-max_part_of_processors-{max_part_of_processors}"
                  f"-length_function-{length_function}-{testing_type}.png")


def research():
    make_research({
        Variable.TASK_NUMBER: 10_000,
        Variable.N_PROCESORS: 100,
        Variable.MAX_LOAD: 0.2,
        Variable.COV: 0.3,
        Variable.LENGTH_FUNCTION: LengthFunctionType.CONCAVE,
        Variable.MAX_PART_OF_PROCESOR_NUMBER: 1.0,
    }, (Variable.COV, [0.3, 1, 2, 5, 10]))
