# Optimize MEMS device geometry by using Genetic Algorithm
Master Thesis of Alan Xu in [MNS lab](https://www.esat.kuleuven.be/mns), ESAT, KU Leuven
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
The parameters `num_generations`, `num_parents_mating`, `mutation_type`, `mutation_num_genes`, `crossover_type`, `parent_selection_type` are all inherited from the [Pygad library](https://pygad.readthedocs.io/en/latest/pygad.html#pygad-ga-class). The constant `CPU_count` indicates how many clients will be created for each session, and `sol_per_pop` should be an integer multiple of `CPU_count` to achieve maximal efficiency. You can also enable the advanced multiprocessing to have a higher degree of multiprocessing, the `sol_per_pop` is no longer constrain to the `CPU_count`. 

## COMSOL models
The COMSOL models could be downloaded and access from [here](https://drive.google.com/drive/folders/15fIS-YFUNZt6R5zCq7ZsJvFv_ob1qcw5?usp=sharing) and please put them to the root directory of the code folder. 

## Existing issue
1. ```python
(r,z,current) = self.model.evaluate(['r','z','es.normJ'])
```
This line of the code is for outputting the value from COMSOL. The $r$, $z$ and current values are one-to-one-mapping from the method evaluation. Therefore, I created a mask (Boolean matrix) on the wanted $r$ and $z$ and then do component-wise multiplication on the current value matrix. The ```evaluate()``` is inherited from [Mph](https://mph.readthedocs.io/en/stable/_modules/mph/model.html#Model.evaluate), and I don't find the way to obtain pre-defined 'Plot' in COMSOL. However, the direct import data from the 'Dataset' in COMSOL with complicated data addressing is not efficient and straightforward. Also, this will hugely increase the workload on manipulating the data. If possible, please refer to the [Manual](https://doc.comsol.com/5.4/doc/com.comsol.help.comsol/COMSOL_ProgrammingReferenceManual.pdf).

2. ```python
charge = self.model.evaluate('es.normD')
```
norm.D can't be evaluate from the COMSOL. This is a bug caused by the COMSOL programming. Avoid evaluating charge density. 
