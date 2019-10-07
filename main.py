from task import Task

if __name__ == '__main__':
    print("Start")
    t = Task(1, 0, 10, 20, 20, lambda z, n: z.base_length / n)
    print(t)
    print(t.calc_length(3))
