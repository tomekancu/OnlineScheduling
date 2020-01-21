from models import Task


# wklesla
def concave_function(task: Task, n: int) -> float:
    return task.base_length / n


# liniowa
def linear_function(task: Task, n: int) -> float:
    max_val = task.base_length / task.min_resources
    min_val = task.base_length / task.max_resources
    len_by_proc = (max_val - min_val) / (task.max_resources - task.min_resources)
    how_shorter = (n - task.min_resources) * len_by_proc
    return max_val - how_shorter


# wypukla
def convex_function(task: Task, n: int) -> float:
    b = task.base_length
    max_n = task.max_resources
    min_n = task.min_resources
    return b / (n - (min_n + max_n)) + b / max_n + b / min_n
