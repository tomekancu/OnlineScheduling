from generator import Generator

if __name__ == '__main__':
    print("Start")
    generator = Generator(10000, (1, 10),
                          (1, 1000), (5000, 6000), 0.1,
                          lambda z, n: z.base_length / n, std_function=lambda x: x * 0.05, save_plots=True)
    tasks = generator.generate()

    for t in tasks[:10]:
        print(t)
        print(t.calc_length(3))
