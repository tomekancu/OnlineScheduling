from generator import Generator
from schedulers.basic import print_scheduling

if __name__ == '__main__':
    print("Start")
    print_scheduling([
        [(0, 1, 0), (1, 3, 1), (3, 4, 4), (5, 8, 3), ],
        [(0, 1, 0), (1, 3, 1), (5, 8, 3), ],
        [(0, 1, 0), (2, 4, 2), (5, 8, 3), ],
    ])

    generator = Generator(10000, (1, 10),
                          (1, 1000), (5000, 6000), 0.1,
                          lambda z, n: z.base_length / n, std_function=lambda x: x * 0.05, print_plots=True)
    tasks = generator.generate()

    for t in tasks[:10]:
        print(t)
        print(t.calc_length(3))
