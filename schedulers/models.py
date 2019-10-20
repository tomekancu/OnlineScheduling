from typing import List, Optional

from task import Task


class ExecutingTask:

    def __init__(self, task: Task, start: float, end: float, assigned_resources: int):
        self.task = task
        self.start = start
        self.end = end
        self.assigned_resources = assigned_resources

    def __str__(self) -> str:
        return f"ExecutingTask(start:{self.start}, end:{self.end}, task:{self.task})"


class Procesor:

    def __init__(self, i: int, tasks: Optional[List[ExecutingTask]] = None):
        self.id = i
        if tasks is None:
            tasks = []
        self.tasks: List[ExecutingTask] = tasks

    def __str__(self) -> str:
        return f"Procesor(id:{self.id}, taks:{self.tasks})"

    def add_task(self, task: ExecutingTask):
        if len(self.tasks) > 0:
            last_task = self.tasks[-1]
            assert last_task.end <= task.start
        self.tasks.append(task)

    def get_next_free_time(self) -> float:
        if len(self.tasks) == 0:
            return 0.0
        last_task = self.tasks[-1]
        return last_task.end

    def is_free(self, when: float) -> bool:
        return self.get_next_free_time() <= when
