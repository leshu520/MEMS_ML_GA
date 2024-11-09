import pygad
import multiprocessing
import comsol_interface 
import json
import logging 
import matplotlib.pyplot as plt  
from numpy import pi
import advanced_multiprocess

# The section below is the definition of the optimization problem
CPU_count = 12
num_generations = 50
num_parents_mating = 8
mutation_num_genes = 1
crossover_type = "single_point" # single_point, two_points, uniform, scattered
parent_selection_type = "sss" # sss, rws, tournament, random
mutation_type = "random" # random, swap, scramble, inversion
sol_per_pop = 12 # assume each CPU can handle one population at a time, but if advanced multiprocessing is used, then sol_per_pop can be set to optimal value. 
Bezier_parameter_name = ['Bezier2r','Bezier2phi','Bezier3phi','BezierWeight1','BezierWeight2','BezierWeight3'] # the weight of the quadratic Bezier curve
# Note: only polar coordinates are used in the Bezier curve (due to the constrain of the COMSOL)
# Due to the relative position of the curve points, change three points is exactly the same as changing two points. 
# we use the rad as the unit for the phi, the range of the phi is from 0 to pi/2
bezier_upper = [3000,pi/2,pi/2,5,5,5]
bezier_lower = [200,0,0,0.2,0.2,0.2]
bezier_step = [100,pi/48,pi/48,0.6,0.6,0.6]

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
# logging configuration 
level = logging.DEBUG
name = 'logfile.txt'

logger = logging.getLogger(name)
logger.setLevel(level)

file_handler = logging.FileHandler(name, 'a+', 'utf-8')
file_handler.setLevel(logging.DEBUG)
file_format = logging.Formatter('%(asctime)s %(levelname)s: %(message)s - %(pathname)s:%(lineno)d', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_format = logging.Formatter('%(message)s')
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)
# The section below is the parallelization of the optimization process
# Since the load mph is quite time consuming, the model loading is done in the worker_init function (abandoned, the data will distorted even with the clear() called). I don't know why, but this is ridiculous.  
# NOTICE: don't edit the parallelization, Python is quite weak in supporting parallelization.
# logging.basicConfig(filename='COMSOL_exception.log', level=logging.ERROR, filemode='w') # rewrite the log file each time, store all errors generate from COSMOL model
pool = None

def worker_init():
    global model 
    model = comsol_interface.Speaker_3D_ComsolInterface('3D_Piezoelectric_Microphone_for_GA_based_Optimization.mph')

def worker_job(solution):
    # arc on the left is the same as the arc on the right, so we only need to optimize the left arc
    if solution[1] >= solution[2]: # create a non-linear constrain to avoid the unexpected connection on slits.
        FOM = 0
    else:
        try:
            model.update(solution)  # Update the model with the solution
            model.run_simulation()  # include build, mesh and solve 
            FOM = model.get_charge_FOM()  # get the figure of merit
        except Exception as e:
            print(f"Error for solution = {solution}") # print if the error occurs
            try: 
                model.run_simulation() # try to run the simulation again
                FOM = model.get_charge_FOM()  # get the figure of merit
            except Exception as e:
                print(f"Error for solution = {solution} again") # print if the error occurs
                print(f"Error message = {e}")
                FOM = 0 # return 0 if there is an error, to avoid any situations like COMSOL model not converging, it's a way to abandon these values
        model.clear() # clear the model to save memory
        model.reset() # reset the model to the initial state
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
    # pool = multiprocessing.Pool(processes=CPU_count, initializer=worker_init)
    # fitness_values = pool.map(worker_job, solutions)
    # enable the advanced multiprocessing by uncommenting the following line
    fitness_values = advanced_multiprocess.boss(solutions)
    return fitness_values

# on generation function shows the results for one generation
last_fitness = 0
# create a list to store the fitness values
all_fitness_over_time = []
# set the range of x axis

plt.xlim(0, num_generations)

def on_generation(ga_instance):
    global last_fitness
    # put the data into the logfile.txt
    ga_instance.logger.info(f"Generation = {ga_instance.generations_completed}")
    ga_instance.logger.info(f"the best Fitness    = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]}")
    ga_instance.logger.info(f"the best Solution   = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[0]}")
    ga_instance.logger.info(f"Change     = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1] - last_fitness}")
    last_fitness = ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]
    all_fitness_over_time.append(ga_instance.last_generation_fitness)
    # draw the fitness plot
    # some memory and multiprocessing issues may occur (pretty random), so we need to use try-except to avoid the program from crashing
    try:
        for i, fitness_values in enumerate(all_fitness_over_time):
            plt.plot([i]*len(fitness_values), fitness_values, 'bo')
        plt.draw()
        plt.pause(5)  # Pause briefly to allow the figure to update
    except Exception as e:
        print(f"Error in plotting the fitness plot. Error message = {e}")
    if ga_instance.generations_completed == ga_instance.num_generations:
        plt.savefig('fitness_plot.png')

gene_space = [{'low': lower_bound[i], 'high': upper_bound[i], 'step': step_values[i]} for i in range(len(upper_bound))]
num_genes = len(upper_bound)

ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating,
                       fitness_batch_size=sol_per_pop,
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
                       save_solutions=True,
                       #keep_elitism=0,
                       #keep_parents=0, # use it cause this gonna be a non-determinstic problems 
                       logger=logger
                       )

if __name__ == '__main__':
    ga_instance.run()
    # ga_instance.plot_fitness(title="Fitness of the best solution in each generation", label="Best Fitness", save_dir="GA_Fitness_plot.png")
    # ga_instance.plot_genes(title="The tendency of the genes in each generation", save_dir="GA_Genes_plot.png") # xlabel and ylabel are not working in this function
    ga_instance.plot_genes(graph_type="histogram", title="Genes histogram", save_dir="GA_Genes_Histogram.png")
    ga_instance.plot_new_solution_rate(title="New Solution Rate in each generation", save_dir="GA_New_Solution_Rate.png")
    shutdown_pool()
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Parameters of the best solution : {solution}".format(solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    config = {"num_generations": num_generations, "num_parents_mating": num_parents_mating, "mutation_num_genes": mutation_num_genes, "crossover_type": crossover_type, "parent_selection_type": parent_selection_type, "sol_per_pop": sol_per_pop, "mutation_type": mutation_type, "CPU_count": CPU_count}
    solution_dicts = [{"parameter": p, "upper_bound": u, "solution": s, "lower_bound": l, "step_value": v} for p, s, u, l, v in zip(parameters_name, solution, upper_bound, lower_bound, step_values)]
    combined_dict = {**config, "solutions": solution_dicts, 'fitness': solution_fitness}
    
    with open('configuration_and_solution.json','w') as f:
        json.dump(combined_dict,f)
    ga_instance.save("genetic") # save the model for the backup 