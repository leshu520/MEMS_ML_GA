import pygad
import numpy
import multiprocessing

from comsol_interface import ACC_ComsolInterface

model = ACC_ComsolInterface('3D_cantilever_beam.mph')

upper_bound = [0.3,0.01,0.03]
lower_bound = [0.1,0.001,0.01]   # they are height, thickness and width of the beam respectively, make sure the alignment is correct
gene_space = [{'low': lower_bound[i], 'high': upper_bound[i]} for i in range(len(upper_bound))]
initial_values = [0.2, 0.005, 0.02]


def fitness_func(ga_instance, solution, solution_idx):    
    model.update(solution)  # Update the model with the solution
    model.run_simulation()  # include build, mesh and solve
    displacement = model.get_displacement()
    fitness_value = max(displacement) # simply take the maximum displacement of the beam
    print(f"Solution {solution_idx} fitness = {fitness_value}")
    return fitness_value  # Fitness value is the maximum displacement of the beam 
    
    """
    # This is an example of a fitness function that can be used with the GA, as this tedency is an example of beam
def fitness_func_test(ga_instance, solution, solution_idx):
    fitness_value = 10*solution[0] - 2*solution[1] + 0.1*solution[2] # height has 10 times more impact than thickness, and thickness has 20 times more impact than width
    return fitness_value
    """

last_fitness = 0
def on_generation(ga_instance):
    global last_fitness
    print(f"Generation = {ga_instance.generations_completed}")
    print(f"Fitness    = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]}")
    print(f"Change     = {ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1] - last_fitness}")
    last_fitness = ga_instance.best_solution(pop_fitness=ga_instance.last_generation_fitness)[1]

num_generations = 50
num_parents_mating = 4

sol_per_pop = 8
num_genes = len(upper_bound)

ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating,
                       fitness_func=fitness_func,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,
                       gene_space=gene_space,
                       on_generation=on_generation)

ga_instance.run()
ga_instance.plot_fitness()

# Returning the details of the best solution.
solution, solution_fitness, solution_idx = ga_instance.best_solution()
print("Parameters of the best solution : {solution}".format(solution=solution))
print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))