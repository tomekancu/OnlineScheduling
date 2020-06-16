from cost_functions import LengthFunctionType, concave_function
from generator import Generator
from models import Task
from plot import print_cost_functions, print_schedulings
from schedulers.choice_shorter_time import ChoiceShorterTimeScheduler
from schedulers.fcfs_with_backfilling import FCFSwithBackfillingScheduler
from schedulers.fair import FairScheduler
from schedulers.base_sita import BaseSITAScheduler
from schedulers.shared_sita import SharedSITAScheduler


def print_cost():
    values = [(en.name, en.get_function()) for en in
              [LengthFunctionType.CONCAVE, LengthFunctionType.CONCAVE_FLAT, LengthFunctionType.CONCAVE_FAST]]
    print_cost_functions(1, 25, 1000, values)


def print_distribution():
    g = Generator(task_number=10000, processors_number=100,
                  coefficient_of_variation=1, max_load=1.0,
                  length_function=LengthFunctionType.CONCAVE,
                  print_plots=True)
    g.generate()


def test1():
    treshold = 8
    n_proc = 4
    instance = [
        Task(0, 0, 1, 10, 10, concave_function),
        Task(1, 2, 1, 2, 10, concave_function),
        Task(2, 2, 1, 1, 10, concave_function),
        Task(3, 10, 1, 3, 4, concave_function),
        Task(4, 9, 1, 3, 3, concave_function),
        Task(5, 7.5, 1, 10, 10, concave_function)
    ]
    schedulers = [
        FCFSwithBackfillingScheduler(),
        ChoiceShorterTimeScheduler(),
        FairScheduler(),
        BaseSITAScheduler(treshold, 0.5),
        SharedSITAScheduler(treshold, 0.5)
    ]

    for scheduler in schedulers:
        scheduler.schedule(n_proc, instance)

    print_schedulings(instance, schedulers, "gantt.png")


def test2():
    treshold = 8
    n_proc = 4
    n_min = 1
    instance = [
        Task(0, 0, n_min, 4, 13, concave_function),
        Task(1, 2, n_min, 4, 4, concave_function),
        Task(2, 2, n_min, 4, 7, concave_function),
        Task(3, 7.5, n_min, 2, 8, concave_function),
        Task(4, 9, n_min, 2, 12, concave_function),
        Task(5, 10, n_min, 4, 10, concave_function),
        Task(6, 12, n_min, 4, 10, concave_function)
    ]
    schedulers = [
        FCFSwithBackfillingScheduler(),
        ChoiceShorterTimeScheduler(),
        FairScheduler(),
        BaseSITAScheduler(treshold, 0.5),
        SharedSITAScheduler(treshold, 0.5)
    ]

    for scheduler in schedulers:
        scheduler.schedule(n_proc, instance)

    print_schedulings(instance, schedulers, "gantt2.png")


def test_load():
    n = 100
    for typ in [LengthFunctionType.CONCAVE, LengthFunctionType.CONCAVE_FAST, LengthFunctionType.CONCAVE_FLAT]:
        for max_load in [0.2, 0.5, 0.8]:
            g = Generator(task_number=1000, processors_number=n,
                          coefficient_of_variation=0.3, max_load=max_load,
                          length_function=typ)
            instance = g.generate()
            scheduler = FairScheduler()
            scheduler.schedule(n, instance)
            metrics = scheduler.calc_metrics()
            print(typ, max_load, metrics.resource_usage)


def test():
    print_cost()
    print_distribution()
    test_load()
    test1()
    test2()
