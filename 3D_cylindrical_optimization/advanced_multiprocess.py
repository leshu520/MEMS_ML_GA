# Description: take reference from the mph library example case, https://github.com/MPh-py/MPh/blob/main/demos/worker_pool.py
from multiprocessing import Process    # external subprocess
from multiprocessing import Queue      # inter-process queue
from multiprocessing import cpu_count  # number of (logical) cores  
from queue import Empty
import time
import comsol_interface

# global variable
workers = 8 # number of workers to hire, the value should be determined by calculating the memory usage for each worker. 
cores = cpu_count() // workers
def worker(jobs, results):
    """Performs jobs and delivers the results."""
    model = comsol_interface.Speaker_3D_ComsolInterface('3D_Piezoelectric_Microphone_for_GA_based_Optimization_shida.mph',cores=cores)
    while True:
        try:
            solution = jobs.get(block=False)
            # print(f"Processing solution")
        except Empty:
            break
        try:  
            model.smart_update(solution)
            model.run_simulation()
            FOM = model.get_charge_FOM()
        except Exception as e: 
            print(f"Error message = {e}")
            FOM = 0
        model.clear()
        model.reset()
        results.put((solution, FOM))

def boss(solutions):
    """Hires workers, assigns jobs, and collects the results."""
    jobs = Queue()
    for solution in solutions:
        jobs.put(solution)

    results = Queue()
    processes = []
    # workers = cpu_count() # if the memory usage is not the bottleneck, you can use the number of logical cores
    for n in range(workers):
        process = Process(target=worker, args=(jobs, results))
        processes.append(process)
        process.start()

    FOMs = []
    for _ in solutions:
        solution, FOM = results.get()
        # print(solution, FOM)
        FOMs.append(FOM)

    for process in processes:
        process.join() # wait for the process to finish

    return FOMs 


if __name__ == '__main__':
    solution = (2.40000000e+03,3.27249235e-01,3.27249235e-01,4.40000000e+00,3.80000000e+00,2.00000000)
    solutions = [solution] * 30
    start_time = time.time()
    FOMs = boss(solutions)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time = {elapsed_time}") 
    print(FOMs)