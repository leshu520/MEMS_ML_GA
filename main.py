import pygad
import multiprocessing
from comsol_interface import ACC_ComsolInterface, Speaker_2D_ComsolInterface

CPU_count = 20
upper_bound = [15,7000,3,2,0.8]
lower_bound = [4,1000,0.5,0.5,0.2]   # they are t_silicon, radius, t_AlN, t_SiO2, electrode ratio respectively, make sure the alignment is correct
step_values = [1,10,0.1,0.1,0.1] # set the discrete values for faster convergence
gene_space = [{'low': lower_bound[i], 'high': upper_bound[i], 'step': step_values[i]} for i in range(len(upper_bound))]

# The section below is the parallelization of the optimization process
# Since the load mph is quite time consuming, the model loading is done in the worker_init function
# NOTICE: don't edit the parallization, Python is quite weak in supporting parallelization, so the code below is quite tricky
pool = None

def worker_init():
    global model 
    model = Speaker_2D_ComsolInterface('2D_Piezoelectric_Microphone_for_GA_based_Optimization.mph')

def initialize_pool():
    global pool
    pool = multiprocessing.Pool(processes=CPU_count, initializer=worker_init)
    print("Process pool has been set up.")

def worker_job(solution):
    try:
        model.update(solution)  # Update the model with the solution
        model.run_simulation()  # include build, mesh and solve 
        FOM = model.get_disp_FOM()  # get the figure of merit
    except:
        print(f"Error for solution = {solution}") # print if the error occurs
        FOM = 0 # return 0 if there is an error, to avoid any situations like COMSOL model not converging, it's a way to abandon these values
    return FOM

def shutdown_pool():
    global pool
    if pool is not None:
        pool.close()
        pool.join()
        pool = None
    print("Process pool has been shut down.")

def fitness_func(ga_instance, solutions, solutions_idx):
    global pool
    print(f"Processing solutions = {solutions_idx}")
    if pool is None:
        initialize_pool()
    fitness_values = pool.map(worker_job,solutions) # type: ignore #dynamically changing the type of the pool
    return fitness_values

last_fitness = 0
def on_generation(ga_instance):
    global last_fitness
    print(f"Generation = {ga_instance.generations_completed}")
    print(f"Fitness    = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]}")
    print(f"Change     = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1] - last_fitness}")
    last_fitness = ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]

num_generations = 100
num_parents_mating = 12

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
                       suppress_warnings=True,
                       save_solutions=True
                       )

if __name__ == '__main__':
    ga_instance.run()
    ga_instance.plot_fitness()
    ga_instance.plot_genes()
    ga_instance.plot_new_solution_rate()
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    shutdown_pool()