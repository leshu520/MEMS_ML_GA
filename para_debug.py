import pygad
import comsol_interface
from multiprocessing import Process    # external subprocess
from multiprocessing import Queue      # inter-process queue
from multiprocessing import cpu_count  # number of (logical) cores
from queue import Empty                # queue-is-empty exception
import numpy as np

def worker(jobs, results):
    model = comsol_interface.Speaker_2D_ComsolInterface('2D_Piezoelectric_Microphone_for_GA_based_Optimization.mph')
    while True:
        try:
            d = jobs.get(block=False)
        except Empty:
            break
        model.update(d)
        model.run_simulation()
        FOM = model.get_current_FOM(1)
        results.put((d, FOM))


def boss():
    jobs = Queue()
    values = np.loadtxt('solution_6.txt')
    for d in values:
        jobs.put(d)


    results = Queue()
    processes = []
    workers = cpu_count()
    for n in range(workers):
        process = Process(target=worker, args=(jobs, results))
        processes.append(process)
        process.start()

    for _ in values: 
        (d, FOM) = results.get()
        print(f'd = {d}, FOM = {FOM}')

if __name__ == '__main__':
    boss()

