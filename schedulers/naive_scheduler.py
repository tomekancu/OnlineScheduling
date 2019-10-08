import math

from task import Task
from typing import List, Set


def linear_scaling(task: Task, workers: int) -> int:
    return math.ceil(task.base_length / workers)


tasks_list = [Task(0, 0, 1, 10, 3, linear_scaling),
              Task(1, 0, 1, 10, 5, linear_scaling),
              Task(2, 2, 1, 10, 4, linear_scaling),
              Task(3, 2, 1, 10, 4, linear_scaling),
              Task(4, 3, 1, 10, 2, linear_scaling)]


def create_schedule(tasks: List[Task], worker_num: int):
    processed_tasks: Set[Task] = set()
    finished_tasks: Set[Task] = set()
    available_workers: int = worker_num
    for current_time in range(10):
        increase_time = True
        available_tasks: Set[Task] = {task for task in tasks if task.ready <= current_time}
        if any([task.min_resources <= available_workers]):
            task: Task = max(available_tasks, key=lambda t: t.base_length)
            proposed_workers = min(task.max_resources, available_workers)
            task.real_length = task.calc_length(proposed_workers)
            task.assigned_resources = int(task.base_length / task.real_length)
            task.start_time = current_time
            task.end_time = current_time + task.real_length
            available_workers -= task.assigned_resources

            processed_tasks.add(task)
            available_tasks.remove(task)

            print(f"Workers: {available_workers}")
            print([str(task) for task in tasks])
            print([str(task) for task in available_tasks])
            print([str(task) for task in processed_tasks])
            print([str(task) for task in finished_tasks])
            return


if __name__ == '__main__':
    create_schedule(tasks_list, 10)
    # print("Start")
    # t = Task(1, 0, 10, 20, 20, lambda z, n: z.base_length / n)
    # print(t)
    # print(t.calc_length(3))
