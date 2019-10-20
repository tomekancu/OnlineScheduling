from task import Task
from generator import Generator
from schedulers.naive import NaiveScheduler
from schedulers.basic import print_scheduling


def cost_function(task: Task, n: int):
    return task.base_length / n


if __name__ == '__main__':
    print("Start")
    instance = [
        Task(0, 0, 1, 10, 10, cost_function),
        Task(1, 2, 1, 2, 10, cost_function),
        Task(2, 2, 1, 1, 10, cost_function),
        Task(4, 10, 1, 3, 3, cost_function),
        Task(3, 11, 3, 3, 4, cost_function),
    ]
    scheduler = NaiveScheduler()
    scheduler.schedule(3, instance)
    print_scheduling(scheduler.procesors)

    generator = Generator(10000, (1, 10),
                          (1, 1000), (5000, 6000), 0.1,
                          lambda z, n: z.base_length / n, std_function=lambda x: x * 0.05, print_plots=True)
    tasks = generator.generate()

    for t in tasks[:10]:
        print(t)
        print(t.calc_length(3))
