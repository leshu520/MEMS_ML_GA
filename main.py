import pygad
import multiprocessing
import comsol_interface 
import json
import logging 
import matplotlib.pyplot as plt 
import numpy as np

# The section below is the definition of the optimization problem
CPU_count = 12
num_generations = 20
num_parents_mating = 8
mutation_num_genes = 1
crossover_type = "single_point" # single_point, two_points, uniform, scattered
parent_selection_type = "sss" # sss, rws, tournament, random
mutation_type = "random" # random, swap, scramble, inversion
sol_per_pop = CPU_count # assume each CPU can handle one population at a time
Bezier_parameter_name = ['Bezier2phi','Bezier3phi','BezierWeight2'] # 1 is the phi of mid point and 2 is the phi of the membrane, 3 is the weight of the quadratic Bezier curve
# Note: only polar coordinates are used in the Bezier curve (due to the constrain of the COMSOL), since the radius of membrane has been included as one of the parameters. The only parameter we can play with is the phi, here the conversion of the polar system to the Cartesian system is introduced.
# we use the rad as the unit for the phi, the range of the phi is from 0 to pi/2 
bezier_upper = [np.pi/3,np.pi/2,2]
bezier_lower = [np.pi/6,0,0.5]
bezier_step = [np.pi/16,np.pi/12,0.1]

# add something that is necessary for the optimization
parameters_name = Bezier_parameter_name
upper_bound = bezier_upper
lower_bound = bezier_lower
step_values = bezier_step # set the discrete values for faster convergence
'''
parameters_name = ['t_silicon','radius','t_AlN','t_SiO2','electrode_ratio']
upper_bound = [15,7000,3,2,0.8] 
lower_bound = [4,1000,0.5,0.5,0.2] 
step_values = [1,100,0.1,0.1,0.1] # set the discrete values for faster convergence
'''

# The section below is the parallelization of the optimization process
# Since the load mph is quite time consuming, the model loading is done in the worker_init function (abandoned, the data will distorted)
# NOTICE: don't edit the parallelization, Python is quite weak in supporting parallelization.
logging.basicConfig(filename='COMSOL_exception.log', level=logging.ERROR, filemode='w') # rewrite the log file each time, store all errors generate from COSMOL model
pool = None

def worker_init():
    global model 
    model = comsol_interface.Speaker_3D_ComsolInterface('3D_Piezoelectric_Microphone_for_GA_based_Optimization.mph')

def worker_job(solution):
    try:
        model.update(solution)  # Update the model with the solution
        model.run_simulation()  # include build, mesh and solve 
        FOM = model.get_stress_FOM()  # get the figure of merit
        model.clear() # clear the model to save memory
        model.reset() # reset the model to the initial state
    except Exception as e:
        print(f"Error for solution = {solution}") # print if the error occurs
        logging.error(f"Error for solution = {solution}. Error message = {e}")
        FOM = 0 # return 0 if there is an error, to avoid any situations like COMSOL model not converging, it's a way to abandon these values
    return FOM

def shutdown_pool():
    global pool
    if pool is not None:
        pool.close()
        pool.join()
        pool = None
    print("Process pool has been shut down.")

# take care of the parallelization data return
def fitness_func(ga_instance, solutions, solutions_idx):
    print(f"Processing solutions = {solutions_idx}")
    pool = multiprocessing.Pool(processes=CPU_count, initializer=worker_init)
    fitness_values = pool.map(worker_job, solutions)
    return fitness_values

# on generation function shows the results for one generation
last_fitness = 0
# create a list to store the fitness values
all_fitness_over_time = []
# set the range of x axis
plt.xlim(0, num_generations)

def on_generation(ga_instance):
    global last_fitness
    print(f"Generation = {ga_instance.generations_completed}")
    print(f"Last Best Fitness  = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]}")
    print(f"Last Best Solution = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[0]}")
    print(f"Change     = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1] - last_fitness}")
    last_fitness = ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]
    all_fitness_over_time.append(ga_instance.last_generation_fitness)
    # draw the fitness plot
    for i, fitness_values in enumerate(all_fitness_over_time):
        plt.plot([i]*len(fitness_values), fitness_values, 'bo')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.title('Fitness of all solution in each generation')
    plt.draw()
    plt.pause(0.5)


gene_space = [{'low': lower_bound[i], 'high': upper_bound[i], 'step': step_values[i]} for i in range(len(upper_bound))]
num_genes = len(upper_bound)

ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating,
                       fitness_batch_size=CPU_count,
                       fitness_func=fitness_func,
                       mutation_num_genes=mutation_num_genes,
                       crossover_type=crossover_type,
                       mutation_type=mutation_type, # type: ignore
                       parent_selection_type=parent_selection_type,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,
                       gene_space=gene_space,
                       on_generation=on_generation,
                       suppress_warnings=True,
                       save_solutions=True
                       )

if __name__ == '__main__':
    ga_instance.run()
    ga_instance.plot_fitness(title="Fitness of the best solution in each generation", label="Best Fitness", save_dir="GA_Fitness_plot.png")
    ga_instance.plot_genes(title="The tendency of the genes in each generation", save_dir="GA_Genes_plot.png") # xlabel and ylabel are not working in this function
    ga_instance.plot_genes(graph_type="histogram", title="Genes histogram", save_dir="GA_Genes_Histogram.png")
    ga_instance.plot_new_solution_rate(title="New Solution Rate in each generation", save_dir="GA_New_Solution_Rate.png")
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    config = {"num_generations": num_generations, "num_parents_mating": num_parents_mating, "mutation_num_genes": mutation_num_genes, "crossover_type": crossover_type, "parent_selection_type": parent_selection_type, "sol_per_pop": sol_per_pop, "mutation_type": mutation_type, "CPU_count": CPU_count}
    solution_dicts = [{"parameter": p, "upper_bound": u, "solution": s, "lower_bound": l, "step_value": v} for p, s, u, l, v in zip(parameters_name, solution, upper_bound, lower_bound, step_values)]
    combined_dict = {**config, "solutions": solution_dicts, 'fitness': solution_fitness}
    
    with open('configuration_and_solution.json','w') as f:
        json.dump(combined_dict,f)
    shutdown_pool()
    ga_instance.save("genetic") # save the model for later use