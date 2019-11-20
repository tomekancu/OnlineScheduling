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
    generator = Generator(task_number=10000, processors_number=20,
                          parameter=0.3, load=1, print_plots=True)
    instance = generator.generate()

    for t in instance[:10]:
        print(t)

    # instance = [
    #     Task(0, 0, 1, 3, 10, cost_function),
    #     Task(1, 2, 1, 2, 10, cost_function),
    #     Task(2, 2, 1, 1, 10, cost_function),
    #     Task(3, 10, 1, 3, 4, cost_function),
    #     Task(4, 11, 1, 3, 3, cost_function),
    # ]

    metrics_all = {}
    for n_proc in range(19, 21):
        print(n_proc)
        metrics = {}

        print("first")
        scheduler1 = NaiveScheduler()
        scheduler1.schedule(n_proc, instance)
        metrics[scheduler1.get_name()] = get_metrics(scheduler1.procesors)

        print("second")
        scheduler2 = SeparateScheduler(5, 0.25)
        scheduler2.schedule(n_proc, instance)
        metrics[scheduler2.get_name()] = get_metrics(scheduler2.procesors)

        print("third")
        scheduler3 = PreemptionScheduler()
        scheduler3.schedule(n_proc, instance)
        metrics[scheduler3.get_name()] = get_metrics(scheduler3.procesors)

        metrics_all[n_proc] = metrics
        # print_schedulings(instance, [scheduler1, scheduler2, scheduler3], "gantt.png")

    print_metrics(metrics_all, "metrics", "metrics.png")
