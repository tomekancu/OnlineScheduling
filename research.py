from typing import Any, List, Dict

from cost_functions import LengthFunctionType
from generator import Generator
from latex import print_latex_plots_for_data
from metrics import Metrics, make_mean_metrics
from data import Variable, Parameters, MetricsDatabase
from plot import print_metrics
from schedulers.abstract import AbstractScheduler
from schedulers.abstract_separate import AbstractSeparateScheduler
from schedulers.choice_shorter_time import ChoiceShorterTimeScheduler
from schedulers.fifo_with_backfilling import FIFOwithBackfillingScheduler
from schedulers.fair import FairScheduler
from schedulers.base_sita import BaseSITAScheduler
from schedulers.shared_sita import SharedSITAScheduler

metrics_database = MetricsDatabase()
metrics_database.load()


def to_plot(default: Parameters, testing_type: Variable, testing_values: List[Any],
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


def print_metrics_for_data(default: Parameters, testing_type: Variable, testing_values: List[Any],
                           schedulers: List[AbstractScheduler]):
    gather = to_plot(default, testing_type, testing_values, schedulers)
    print_metrics(gather,
                  f"metrics max_load{default.max_load} cov{default.cov} "
                  f"length_function{default.length_function} {testing_type}",
                  file=f"temp/metrics-plot.png")


def make_research(default: Parameters, testing_type: Variable, testing_values: List[Any],
                  schedulers: List[AbstractScheduler]):
    default.print()
    print(f"testing_type={testing_type}, testing_values={testing_values}")
    for test_id in range(default.test_number):
        print(f"test: {test_id}")
        for val in testing_values:
            print(f"test: {test_id} testing: {val}")
            params = default.make_instance_for(testing_type, val)
            gen = Generator(task_number=params.task_number, processors_number=params.n_procesors,
                            coefficient_of_variation=params.cov, max_load=params.max_load,
                            length_function=params.length_function,
                            print_plots=False)
            instance = gen.generate()

            collected_metrics = {}
            max_max_end = 0
            for i, scheduler in enumerate(schedulers):
                if isinstance(scheduler, AbstractSeparateScheduler):
                    scheduler.task_size_treshold = gen.get_mid_task_size()
                name = scheduler.get_name()
                print(f"test: {test_id} testing: {val} i: {i + 1}/{len(schedulers)} alg: {name}")
                in_database = metrics_database.get_metrics(params, name)
                if len(in_database) < default.test_number:
                    scheduler.schedule(params.n_procesors, instance)
                    metrics = scheduler.calc_metrics()
                    max_max_end = max(max_max_end, metrics.max_end)
                    collected_metrics[name] = metrics
            for name, metrics in collected_metrics.items():
                metrics.set_arl(max_max_end)
                metrics_database.save_metric(params, name, metrics)
            metrics_database.save()


ALL_COV = [0.3, 1, 2, 5, 10]
ALL_PERCENT = [0.2, 0.4, 0.6, 0.8, 1.0]


def print_all_latex_plot():
    schedulers = [
        FIFOwithBackfillingScheduler(),
        ChoiceShorterTimeScheduler(),
        FairScheduler(),
        BaseSITAScheduler(0, 0.25),
        BaseSITAScheduler(0, 0.5),
        BaseSITAScheduler(0, 0.75),
        SharedSITAScheduler(0, 0.25),
        SharedSITAScheduler(0, 0.5),
        SharedSITAScheduler(0, 0.75),
    ]
    for lf_name, length_function in [
        ("pe", LengthFunctionType.CONCAVE),
        ("ps", LengthFunctionType.CONCAVE_FLAT),
        ("pr", LengthFunctionType.CONCAVE_FAST)
    ]:
        for variable_type, changes, second_value in [
            (Variable.COV, ALL_COV, 1.0),
            (Variable.COV, ALL_COV, 0.2),
            (Variable.MAX_LOAD, ALL_PERCENT, 0.3),
            (Variable.MAX_LOAD, ALL_PERCENT, 10)
        ]:
            if variable_type == Variable.COV:
                parameters = Parameters(test_number=3, n_procesors=100, task_number=10_000,
                                        max_load=second_value, cov=10, length_function=length_function)
                filename = f"temp/d-cov-rho-{second_value}-{lf_name}.tex"
            else:
                parameters = Parameters(test_number=3, n_procesors=100, task_number=10_000,
                                        max_load=0.2, cov=second_value, length_function=length_function)
                filename = f"temp/d-load-cov-{second_value}-{lf_name}.tex"
            print_latex_plots_for_data(metrics_database, parameters, variable_type, changes, schedulers, filename)


def research():
    print_all_latex_plot()
    for length_function in [
        LengthFunctionType.CONCAVE,
        LengthFunctionType.CONCAVE_FLAT,
        LengthFunctionType.CONCAVE_FAST
    ]:
        schedulers = [
            FIFOwithBackfillingScheduler(),
            ChoiceShorterTimeScheduler(),
            FairScheduler(),
            BaseSITAScheduler(0, 0.25),
            BaseSITAScheduler(0, 0.5),
            BaseSITAScheduler(0, 0.75),
            SharedSITAScheduler(0, 0.25),
            SharedSITAScheduler(0, 0.5),
            SharedSITAScheduler(0, 0.75),
        ]
        parameters = Parameters(test_number=3, n_procesors=100, task_number=10_000,
                                max_load=1.0, cov=10, length_function=length_function)
        make_research(parameters, Variable.COV, ALL_COV, schedulers)
        parameters = Parameters(test_number=3, n_procesors=100, task_number=10_000,
                                max_load=0.2, cov=10, length_function=length_function)
        make_research(parameters, Variable.COV, ALL_COV, schedulers)
        parameters = Parameters(test_number=3, n_procesors=100, task_number=10_000,
                                max_load=0.2, cov=0.3, length_function=length_function)
        make_research(parameters, Variable.MAX_LOAD, ALL_PERCENT, schedulers)
        parameters = Parameters(test_number=3, n_procesors=100, task_number=10_000,
                                max_load=0.2, cov=10, length_function=length_function)
        make_research(parameters, Variable.MAX_LOAD, ALL_PERCENT, schedulers)
