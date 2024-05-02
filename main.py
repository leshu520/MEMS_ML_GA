import pygad
import numpy
import multiprocessing
from comsol_interface import ACC_ComsolInterface

CPU_count = 24
upper_bound = [0.5,0.01,0.03]
lower_bound = [0.15,0.001,0.01]   # they are height, thickness and width of the beam respectively, make sure the alignment is correct
gene_space = [{'low': lower_bound[i], 'high': upper_bound[i]} for i in range(len(upper_bound))]
# think about discretizing the gene space to make the search more efficient

pool = None

def worker_init():
    global model 
    model = ACC_ComsolInterface('3D_cantilever_beam.mph')

def initialize_pool():
    global pool
    pool = multiprocessing.Pool(processes=CPU_count, initializer=worker_init)

def worker_job(solution):
    print(f"Processing job for solution = {solution}")
    model.update(solution)  # Update the model with the solution
    model.run_simulation()  # include build, mesh and solve 
    return max(model.get_displacement()) # simply take the maximum displacement of the beam

def fitness_func(ga_instance, solutions, solutions_idx):
    global pool
    if pool is None:
        initialize_pool()
    fitness_values = pool.map(worker_job, solutions) # type: ignore #dynamically changing the type of the pool
    return fitness_values

last_fitness = 0
def on_generation(ga_instance):
    global last_fitness
    print(f"Generation = {ga_instance.generations_completed}")
    print(f"Fitness    = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]}")
    print(f"Change     = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1] - last_fitness}")
    last_fitness = ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]

num_generations = 20
num_parents_mating = 16

sol_per_pop = CPU_count
num_genes = len(upper_bound)

ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating,
                       fitness_batch_size=CPU_count,
                       fitness_func=fitness_func,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,
                       gene_space=gene_space,
                       on_generation=on_generation,
                       # parallel_processing=24, not able to use, error: Cannot access client instance from different thread. probably there are some crosstalk between the threads of the comsol 
                       save_solutions=True)

if __name__ == '__main__':
    ga_instance.run()
    ga_instance.plot_fitness()
    ga_instance.plot_genes()
    ga_instance.plot_new_solution_rate()
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))