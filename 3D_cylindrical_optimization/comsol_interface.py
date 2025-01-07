import mph
import numpy as np
import time 

class ComsolInterface:
    def __init__(self, model_path, cores=1):
        self.client = mph.start(cores=cores) 
        self.cores = cores
        try:
            self.model = self.client.load(model_path)
            self.model_path = model_path
            # print("Loaded model on", self.cores, "core(s):", self.client.models())
        except Exception as e:
            print("Error: Could not load the model.", e)
            exit()

    def run_simulation(self):
        self.model.mesh() # Mesh the geometry
        self.model.solve() # normally there is only one study
        return self.model

    def clear(self):
        self.model.clear() # Clear disk space for history and results

    def set_parameter(self, name, value):
        self.model.parameter(name=name, value=value) # Set the parameter of the model, name is the name of the parameter, value is the value of the parameter

    def build(self):
        self.model.build()  # Build the model after setting the parameter

    def reset(self):
        self.model.reset() 

class ACC_ComsolInterface(ComsolInterface):    
    def get_displacement(self):
        return self.model.evaluate('solid.disp','mm') 
    
    def update(self, solution): # update the model with the solution, specifically the height, thickness and width of the beam
        self.set_parameter('H', solution[0])
        self.set_parameter('Thickn', solution[1])
        self.set_parameter('W', solution[2])
        self.build()
        return self.model
    
class Speaker_2D_ComsolInterface(ComsolInterface):
    frequency_steps = 40 # the number of frequency steps in the simulation. Change if the model study steps is changed
    def get_disp_FOM(self):
        displacement = self.model.evaluate('solid.disp','mm') # as we know the frequency simulation range is from 100Hz to 80kHz with step size of 500Hz, so we can have a FOM from 20Hz to 20kHz by manually selecting the array from 0 to 40
        FOM = sum(displacement[0:self.frequency_steps][:,0]) # sum them up as integral, first column is the spatial coordinator at (0,0,0) 
        return FOM
    
    def create_AlN_mask(self, r, z): # create a mask for the AlN layer
        r_min, r_max = 0, self.r_electrode # generate the min and max radius of the ALN
        z_min, z_max = self.t_silicon + self.t_SiO2, self.t_silicon + self.t_SiO2 + self.t_AlN # generate the min and max height of the AlN
        mask = (r[0:self.frequency_steps] >= r_min) & (r[0:self.frequency_steps] <= r_max) & (z[0:self.frequency_steps] >= z_min) & (z[0:self.frequency_steps] <= z_max) # Create the mask for the ALN
        return mask
    
    def create_electrode_mask(self, r, z): # create a mask for the electrode layer
        r_min, r_max = self.r_electrode, self.radius # generate the min and max radius of the electrode
        z_min, z_max = self.t_silicon + self.t_SiO2, self.t_silicon + self.t_SiO2 + self.t_AlN # generate the min and max height of the electrode
        mask = (r[0:self.frequency_steps] >= r_min) & (r[0:self.frequency_steps] <= r_max) & (z[0:self.frequency_steps] >= z_min) & (z[0:self.frequency_steps] <= z_max) # Create the mask for the electrode
        return mask
    
    def get_stress_FOM(self,selection=1):
        (r,z,stress) = self.model.evaluate(['r','z','solid.mises_peak']) # using peak value is not accurate 
        if selection == 1:
            mask = self.create_AlN_mask(r,z)
        elif selection == 2:
            mask = self.create_electrode_mask(r,z) # Create the mask for the ALN
        filtered_stress = stress[0:self.frequency_steps][mask]
        FOM = sum(filtered_stress) # sum up the displacement to get the figure of merit in frequency 20Hz to 20kHz
        return FOM

    def get_current_FOM(self,selection=1): # the all current of the ALN layer
        (r,z,current) = self.model.evaluate(['r','z','es.normJ']) # return unit is A/m^2
        current_non_nan = np.nan_to_num(current, nan=0.0)
        if selection == 1: 
            mask = self.create_AlN_mask(r,z) # Create the mask for the ALN
        elif selection == 2: 
            mask = self.create_electrode_mask(r,z)
        filtered_current = current_non_nan[0:self.frequency_steps][mask]
        FOM = sum(filtered_current) # sum up the current to get the figure of merit in frequency 20Hz to 20kHz
        return FOM
    
    def get_charge_FOM(self,selection=1): # es.nD is not working here I use normD instead
        (r,z,charge) = self.model.evaluate(['r','z','es.normD'])
        charge_non_nan = np.nan_to_num(charge, nan=0.0) 
        if selection == 1:
            mask = self.create_AlN_mask(r,z) # Create the mask for the ALN
        elif selection == 2:
            mask = self.create_electrode_mask(r,z) # Create the mask for the electrode
        filtered_charge = charge_non_nan[0:self.frequency_steps][mask]
        FOM = sum(filtered_charge)
        return FOM

    def update(self, solution): # store the values of the solution and update the model with the solution
        self.t_silicon, self.radius, self.t_AlN, self.t_SiO2, r_electrode_factor = solution
        self.r_electrode = r_electrode_factor * self.radius
        self.set_parameter('t_silicon',f'{self.t_silicon}[um]')
        self.set_parameter('radius',f'{self.radius}[um]')
        self.set_parameter('t_AlN',f'{self.t_AlN}[um]')
        self.set_parameter('t_SiO2',f'{self.t_SiO2}[um]')
        self.set_parameter('r_electrode',f'{(self.r_electrode)}[um]')
        self.build()
        return self.model
    
class Speaker_3D_ComsolInterface(ComsolInterface):
    frequency_steps = 40 # the simulation step size has been set as 500Hz
    # these values have been defined in the model and would not be changed during the optimization simulation process.
    # If I use get_parameter() there is possibility for the unit conversion error. Make sure these values are the same in the model 
    t_silicon = 12
    radius = 3200
    t_SiO2 = 0.7
    r_electrode = 0.7 * radius
    t_AlN = 0.5

    def update(self, solution): # store the values of the solution and update the model with the solution
        self.bezier = solution
        # before inject the values to the model, we need to convert the polar coordinates to the Cartesian coordinates
        self.bezier2x, self.bezier2y = self.polar_to_cartesian(self.bezier[0], self.bezier[1])
        # 1.02 here is used to cast the Bezier curve to the outside of the membrane (at the edge may cause the division unfinished)
        self.bezier3x, self.bezier3y = self.polar_to_cartesian(self.radius*1.02 , self.bezier[2])
        self.set_parameter('Bezier2x',f'{self.bezier2x}[um]')
        self.set_parameter('Bezier2y',f'{self.bezier2y}[um]')
        self.set_parameter('Bezier3x',f'{self.bezier3x}[um]')
        self.set_parameter('Bezier3y',f'{self.bezier3y}[um]')
        self.set_parameter('BezierWeight1',f'{self.bezier[3]}')
        self.set_parameter('BezierWeight2',f'{self.bezier[4]}')
        self.set_parameter('BezierWeight3',f'{self.bezier[5]}')
        self.build()
        return self.model

    def smart_update(self,solution):
        self.bezier = solution
        self.bezier2x, self.bezier2y = self.polar_to_cartesian(self.bezier[0], self.bezier[1])
        self.set_parameter('Bezier2x',f'{self.bezier2x}[um]')
        self.set_parameter('Bezier2y',f'{self.bezier2y}[um]')
        self.set_parameter('BezierWeight1',f'{self.bezier[2]}')
        self.set_parameter('BezierWeight2',f'{self.bezier[3]}')
        self.set_parameter('BezierWeight3',f'{self.bezier[4]}')
        self.set_parameter('Bezier1x',f'{self.bezier[5]}[um]')
        self.build()
        return self.model 

    # this method has severe issue, the solid.misesGp can't be used directly
    def get_stress_FOM(self):
        [x,y,z,stress] = self.model.evaluate(['x','y','z','solid.misesGp'])
        mask = self.create_AlN_mask(x*1e6,y*1e6,z*1e6) # need to work with the unit of the COMSOL model (default is m) and here is um
        filtered_stress = stress[mask]
        FOM = sum(filtered_stress)
        return FOM
    
    def get_charge_FOM(self):
        [x,y,z,charge] = self.model.evaluate(['x','y','z','es.normD'])
        mask = self.create_AlN_mask(x*1e6,y*1e6,z*1e6)
        charge_non_nan = np.nan_to_num(charge, nan=0.0)                             
        filtered_charge = charge_non_nan[mask]
        FOM = sum(filtered_charge)
        return FOM 
    
        # create the 3D mask is bit tricky, convert to the polar coordinates.  
    def create_AlN_mask(self,x,y,z):
        r_min, r_max = 0, self.r_electrode # generate the min and max radius of the ALN
        z_min, z_max = self.t_silicon + self.t_SiO2, self.t_silicon + self.t_SiO2 + self.t_AlN # generate the min and max height of the AlN
        r = self.cartesian_to_polar(x,y)
        mask = (r >= r_min) & (r <= r_max) & (z >= z_min) & (z <= z_max)
        return mask
    
    def create_top_mask(self,x,y,z):
        z_min, z_max = self.t_silicon + self.t_SiO2, self.t_silicon + self.t_SiO2 + self.t_AlN # generate the min and max height of the AlN
        mask = (z > z_min) & (z < z_max)
        return mask
    
    def get_charge_FOM_faster(self):
        [z,charge] = self.model.evaluate(['z','es.normD'])
        mask = self.create_top_mask(z*1e6)
        charge_non_nan = np.nan_to_num(charge, nan=0.0)  
        filtered_charge = charge_non_nan[mask]
        FOM = sum(filtered_charge)
        return FOM
    
    # conversion based on the numpy library, use rad as the unit for the phi 
    def polar_to_cartesian(self,r,phi):
        x = r * np.cos(phi)
        y = r * np.sin(phi)
        return x, y
    
    def cartesian_to_polar(self,x,y):
        r = np.sqrt(x**2 + y**2)
        return r


# test code for the data read and set functions, useful debug tool
# 1 for the multiple simulation, 2 for the single simulation, 3 for the 3D simulation, 4 to test the bassline model
if __name__ == '__main__':
    selection_multiple = 3
    if (selection_multiple==1):
        model = Speaker_2D_ComsolInterface('2D_Piezoelectric_Microphone_for_GA_based_Optimization.mph',cores=24)
        solution = np.loadtxt('solution_6.txt')
        for i in range(24):
            model.update(solution[i])
            model.run_simulation()
            print(model.get_stress_FOM(selection=1))
            model.clear()
            model.reset() 
    elif (selection_multiple==2):
        model = Speaker_2D_ComsolInterface('2D_Piezoelectric_Microphone_for_GA_based_Optimization.mph',cores=24)
        solution = [11,3200,0.6,1.9,0.7]
        model.update(solution)
        model.run_simulation()
        print(model.get_charge_FOM(selection=1))   
        model.clear()
        model.reset()
    elif (selection_multiple==3):
        model = Speaker_3D_ComsolInterface('3D_Piezoelectric_Microphone_for_GA_based_Optimization_shida.mph',cores=24)
        solution = (2600,1.439,0.4,0.8,0.8)
        model.smart_update(solution)  
        print(f"2x and 2y are:", model.polar_to_cartesian(solution[0],solution[1]))
        model.model.save()
        start_time = time.time()
        for i in range(30):
            try:
                model.run_simulation()
                print(model.get_charge_FOM())
            except Exception as e: 
                print(f"Error in processing solution")
            model.clear()
            model.reset()
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed time = {elapsed_time}")
        # 10408 seconds
    elif (selection_multiple==4):
        model = Speaker_3D_ComsolInterface('3D_Piezoelectric_Microphone_for_GA_based_Optimization_shida.mph',cores=24)
        model.run_simulation()
        print(model.get_charge_FOM())
        model.clear()
        model.reset()
        