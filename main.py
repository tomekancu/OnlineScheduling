from models import Task
from generator import Generator
from schedulers.naive import NaiveScheduler
from schedulers.separate import SeparateScheduler
from schedulers.preemption import PreemptionScheduler
from plot import print_schedulings, print_metrics
from metrics import get_metrics


def cost_function(task: Task, n: int):
    return task.base_length / n


if __name__ == '__main__':
    print("Start")

    metrics_all = {}
    for max_load in [0.2, 0.4, 0.6, 0.8, 1.0]:
        n_procesors = 100
        generator = Generator(task_number=1000, processors_number=n_procesors,
                              coefficient_of_variation=0.3, max_load=max_load, max_part_of_processors_number=1.0,
                              print_plots=False)
        instance = generator.generate()
        print(max_load)
        metrics = {}

        print("first")
        scheduler1 = NaiveScheduler()
        scheduler1.schedule(n_procesors, instance)
        metrics[scheduler1.get_name()] = get_metrics(scheduler1.procesors)

        print("second25")
        scheduler2 = SeparateScheduler(generator.get_mid_task_size(), 0.25)
        scheduler2.schedule(n_procesors, instance)
        metrics[scheduler2.get_name()] = get_metrics(scheduler2.procesors)

        print("second50")
        scheduler3 = SeparateScheduler(generator.get_mid_task_size(), 0.50)
        scheduler3.schedule(n_procesors, instance)
        metrics[scheduler3.get_name()] = get_metrics(scheduler3.procesors)

        print("second75")
        scheduler4 = SeparateScheduler(generator.get_mid_task_size(), 0.75)
        scheduler4.schedule(n_procesors, instance)
        metrics[scheduler4.get_name()] = get_metrics(scheduler4.procesors)

        print("third")
        scheduler5 = PreemptionScheduler()
        scheduler5.schedule(n_procesors, instance)
        metrics[scheduler5.get_name()] = get_metrics(scheduler5.procesors)

        metrics_all[max_load] = metrics
        # print_schedulings(instance, [scheduler1, scheduler2, scheduler3], "gantt.png")

    print_metrics(metrics_all, "metrics", "metrics.png")
