from cost_functions import LengthFunctionType, concave_function
from generator import Generator
from models import Task
from plot import print_cost_functions, print_schedulings
from schedulers.naive import NaiveScheduler
from schedulers.preemption import PreemptionScheduler
from schedulers.separate import SeparateScheduler
from schedulers.separate_with_premption import SeparateWithPremptionScheduler


def print_cost():
    values = [(en.get_name(), en.get_function()) for en in
              [LengthFunctionType.CONCAVE, LengthFunctionType.CONCAVE_FLAT]]
    print_cost_functions(1, 25, 1000, values)


def print_distribution():
    g = Generator(task_number=10000, processors_number=100,
                  coefficient_of_variation=1, max_load=1.0,
                  length_function=concave_function,
                  max_part_of_processors_number=1.0,
                  print_plots=True)
    g.generate()


def test1():
    instance = [
        Task(0, 0, 1, 10, 10, concave_function),
        Task(1, 2, 1, 2, 10, concave_function),
        Task(2, 2, 1, 1, 10, concave_function),
        Task(3, 10, 1, 3, 4, concave_function),
        Task(4, 9, 1, 3, 3, concave_function),
        Task(5, 7.5, 1, 10, 10, concave_function)
    ]
    treshold = 8
    n_proc = 4
    scheduler1 = NaiveScheduler()
    scheduler1.schedule(n_proc, instance)

    scheduler2 = SeparateScheduler(treshold, 0.5)
    scheduler2.schedule(n_proc, instance)

    scheduler3 = SeparateWithPremptionScheduler(treshold, 0.5)
    scheduler3.schedule(n_proc, instance)

    scheduler4 = PreemptionScheduler()
    scheduler4.schedule(n_proc, instance)

    print_schedulings(instance, [scheduler1, scheduler2, scheduler3, scheduler4], "gantt.png")


def test2():
    treshold = 8
    n_proc = 4
    n_min = 1
    n_max = int(1.0 * n_proc)
    instance = [
        Task(0, 0, n_min, n_max, 13, concave_function),
        Task(1, 2, n_min, n_max, 4, concave_function),
        Task(2, 2, n_min, n_max, 7, concave_function),
        Task(3, 10, n_min, n_max, 10, concave_function),
        Task(4, 9, n_min, n_max, 12, concave_function),
        Task(5, 7.5, n_min, n_max, 11, concave_function)
    ]
    scheduler1 = NaiveScheduler()
    scheduler1.schedule(n_proc, instance)

    scheduler2 = SeparateScheduler(treshold, 0.5)
    scheduler2.schedule(n_proc, instance)

    scheduler3 = SeparateWithPremptionScheduler(treshold, 0.5)
    scheduler3.schedule(n_proc, instance)

    scheduler4 = PreemptionScheduler()
    scheduler4.schedule(n_proc, instance)

    print_schedulings(instance, [scheduler1, scheduler2, scheduler3, scheduler4], "gantt2.png")


def test():
    print_cost()
    print_distribution()
    test1()
    test2()
