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
    # generator = Generator(10000, (1, 10),
    #                       (1, 1000), (5000, 6000), 0.1,
    #                       (500, 50),
    #                       lambda z, n: z.base_length / n, print_plots=True)
    # tasks = generator.generate()
    #
    # for t in tasks[:10]:
    #     print(t)
    #     print(t.calc_length(3))

    instance = [
        Task(0, 0, 1, 3, 10, cost_function),
        Task(1, 2, 1, 2, 10, cost_function),
        Task(2, 2, 1, 1, 10, cost_function),
        Task(3, 10, 1, 3, 4, cost_function),
        Task(4, 11, 1, 3, 3, cost_function),
    ]

    metrics_all = {}
    for n_proc in range(2, 5):
        metrics = {}
        scheduler1 = NaiveScheduler()
        scheduler1.schedule(n_proc, instance)
        metrics[scheduler1.get_name()] = get_metrics(scheduler1.procesors)

        scheduler2 = SeparateScheduler(5, 0.25)
        scheduler2.schedule(n_proc, instance)
        metrics[scheduler2.get_name()] = get_metrics(scheduler2.procesors)

        scheduler3 = PreemptionScheduler()
        scheduler3.schedule(n_proc, instance)
        metrics[scheduler3.get_name()] = get_metrics(scheduler3.procesors)

        metrics_all[n_proc] = metrics
        print_schedulings(instance, [scheduler1, scheduler2, scheduler3], "gantt.png")

    print_metrics(metrics_all, "metrics", "metrics.png")
