import pygad
import numpy

def fitness_func(solution, solution_idx):
    fitness = numpy.sum(solution)
    return fitness

def run_ga():
    # 定义遗传算法的参数
    ga_instance = pygad.GA(num_generations=50,
                           num_parents_mating=5,
                           fitness_func=fitness_func,
                           sol_per_pop=10,
                           num_genes=5,
                           init_range_low=-5,
                           init_range_high=5)

    ga_instance.run()

if __name__ == "__main__":
    run_ga()