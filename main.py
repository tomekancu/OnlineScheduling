from models import Task
from generator import Generator
from schedulers.naive import NaiveScheduler
from schedulers.preemption import PreemptionScheduler
from plot import print_schedulings


def cost_function(task: Task, n: int):
    return task.base_length / n


if __name__ == '__main__':
    print("Start")
    instance = [
        Task(0, 0, 1, 3, 10, cost_function),
        Task(1, 2, 1, 2, 10, cost_function),
        Task(2, 2, 1, 1, 10, cost_function),
        Task(3, 10, 1, 3, 4, cost_function),
        Task(4, 11, 1, 3, 3, cost_function),
    ]
    n_proc = 4
    scheduler = NaiveScheduler()
    scheduler.schedule(n_proc, instance)

    scheduler2 = PreemptionScheduler()
    scheduler2.schedule(n_proc, instance)
    print_schedulings(instance, [scheduler, scheduler2], "gantt.png")

    # generator = Generator(10000, (1, 10),
    #                       (1, 1000), (5000, 6000), 0.1,
    #                       lambda z, n: z.base_length / n, std_function=lambda x: x * 0.05, print_plots=True)
    # tasks = generator.generate()
    #
    # for t in tasks[:10]:
    #     print(t)
    #     print(t.calc_length(3))
