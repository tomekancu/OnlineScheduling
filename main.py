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
    n_procesors = 100
    max_load = 0.5
    cov = 2  # 0.3 1 2 5 10
    for max_res in [0.25, 0.5, 0.75, 1.0, 1.25]:
        print(max_res)
        generator = Generator(task_number=1000, processors_number=n_procesors,
                              coefficient_of_variation=cov, max_load=max_load, max_part_of_processors_number=max_res,
                              print_plots=False)
        instance = generator.generate()
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

        metrics_all[max_res] = metrics
        # print_schedulings(instance, [scheduler1, scheduler2, scheduler3], "gantt.png")

    print_metrics(metrics_all,
                  f"metrics max_load{max_load} cov{cov} max_res",
                  f"metrics-max-load-{max_load}-cov{cov}-max-res.png")
