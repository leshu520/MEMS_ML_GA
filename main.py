import pygad
import numpy
import multiprocessing

from comsol_interface import ACC_ComsolInterface

model = ACC_ComsolInterface('3D_cantilever_beam.mph')
model.set_parameter('W', '0.03')
model.run_simulation()
displacement = model.get_displacement()
print("Displacement: ", max(displacement))
model.set_parameter('W', '0.01')
model.run_simulation()
displacement = model.get_displacement()
print("Displacement: ", max(displacement))
model.clear()