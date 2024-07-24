# Optimize MEMS device geometry by using Genetic Algorithm
Master Thesis of Alan Xu in MNS lab, ESAT, KU Leuven
## NOTICE! 
1. The Python version from the Microsoft Store may not work correctly with this project. It is recommended to download Python from the [official Python website](https://www.python.org/downloads/). 
## Files
1. **Log files**: These files are generated in the root directory and contain information about potential errors during the COMSOL simulation.
2. **.pkl files**: These files can be loaded for Pygad. For more details, please check the [Pygad documentation](https://pygad.readthedocs.io/en/latest/pygad.html#functions-in-pygad).
3. **JSON files**: The best solution and GA configuration are written to a JSON file in the root directory.
4. **.png files**: Plots. 
## Dependencies
This project relies on the following Python libraries:

1. [Mph](https://mph.readthedocs.io/en/stable/): A Python library for controlling COMSOL Multiphysics simulations. In this project, it is used to manage the COMSOL simulation process.
2. [Pygad](https://pygad.readthedocs.io/en/latest/): A Python library for implementing the genetic algorithm. In this project, it is used to optimize the MEMS device geometry.

You can install these dependencies by running the following commands in your terminal:

```bash
pip install mph
pip install pygad

```
## Genetic Algorithm Configuration
The parameters `num_generations`, `num_parents_mating`, `mutation_type`, `mutation_num_genes`, `crossover_type`, `parent_selection_type` are all inherited from the [Pygad library](https://pygad.readthedocs.io/en/latest/pygad.html#pygad-ga-class). The constant `CPU_count` indicates how many clients will be created for each session, and `sol_per_pop` should be an integer multiple of `CPU_count` to achieve maximal efficiency.

## COMSOL models
The COMSOL models could be downloaded and access from [here](https://drive.google.com/drive/folders/15fIS-YFUNZt6R5zCq7ZsJvFv_ob1qcw5?usp=sharing) and put them to the root directionary of the code folder. 