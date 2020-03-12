from cost_functions import LengthFunctionType, concave_function
from generator import Generator
from models import Task
from plot import print_cost_functions, print_schedulings
from schedulers.choice_shorter_time import ChoiceShorterTimeScheduler
from schedulers.get_max import GetMaxScheduler
from schedulers.paralleled_if_possible import ParalleledIfPossibleScheduler
from schedulers.sita import SITAScheduler
from schedulers.shared_sita import SharedSITAScheduler


def print_cost():
    values = [(en.get_name(), en.get_function()) for en in
              [LengthFunctionType.CONCAVE, LengthFunctionType.CONCAVE_FLAT, LengthFunctionType.CONCAVE_FAST]]
    print_cost_functions(1, 25, 1000, values)


def print_distribution():
    g = Generator(task_number=10000, processors_number=100,
                  coefficient_of_variation=1, max_load=1.0,
                  length_function=concave_function,
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
        GetMaxScheduler(),
        ChoiceShorterTimeScheduler(),
        ParalleledIfPossibleScheduler(),
        SITAScheduler(treshold, 0.5),
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
        GetMaxScheduler(),
        ChoiceShorterTimeScheduler(),
        ParalleledIfPossibleScheduler(),
        SITAScheduler(treshold, 0.5),
        SharedSITAScheduler(treshold, 0.5)
    ]

    for scheduler in schedulers:
        scheduler.schedule(n_proc, instance)

    print_schedulings(instance, schedulers, "gantt2.png")


def test():
    print_cost()
    print_distribution()
    test1()
    test2()
