from cost_functions import concave_function
from models import Task
from generator import Generator
from schedulers.naive import NaiveScheduler
from schedulers.separate import SeparateScheduler
from schedulers.preemption import PreemptionScheduler
from schedulers.separate_with_premption import SeparateWithPremptionScheduler
from plot import print_schedulings, print_metrics
from metrics import get_metrics


def research():
    metrics_all = {}
    n_procesors = 100
    max_load = 0.2
    cov = 2  # 0.3 1 2 5 10
    for cov in [0.3, 1, 2, 5, 10]:
        print(cov)
        n = 10000
        if cov > 2:
            n = 10000
        gen = Generator(task_number=n, processors_number=n_procesors,
                        coefficient_of_variation=cov, max_load=max_load,
                        length_function=concave_function,
                        max_part_of_processors_number=1.0,
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

        print("second50")
        scheduler3 = SeparateScheduler(gen.get_mid_task_size(), 0.50)
        scheduler3.schedule(n_procesors, instance)
        metr[scheduler3.get_name()] = get_metrics(scheduler3.procesors)

        print("second75")
        scheduler4 = SeparateScheduler(gen.get_mid_task_size(), 0.75)
        scheduler4.schedule(n_procesors, instance)
        metr[scheduler4.get_name()] = get_metrics(scheduler4.procesors)

        print("third")
        scheduler5 = PreemptionScheduler()
        scheduler5.schedule(n_procesors, instance)
        metr[scheduler5.get_name()] = get_metrics(scheduler5.procesors)

        metrics_all[cov] = metr
        # print_schedulings(instance, [scheduler1, scheduler2, scheduler3], "gantt.png")
    print_metrics(metrics_all,
                  f"metrics max_load{max_load} cov",
                  f"metrics-max-load-{max_load}-cov.png")


def test():
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

    print_schedulings(instance, [scheduler1, scheduler2, scheduler3, scheduler4])


if __name__ == '__main__':
    print("Start")
    test()
