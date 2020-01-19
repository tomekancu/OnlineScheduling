from models import Task


# wklesla
def concave_function(task: Task, n: int) -> float:
    return task.base_length / n


# liniowa
def linear_function(task: Task, n: int) -> float:
    return task.base_length / n


# wypukla
def convex_function(task: Task, n: int) -> float:
    return task.base_length / n
