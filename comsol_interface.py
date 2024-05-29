import mph
import numpy as np

class ComsolInterface:
    def __init__(self, model_path, cores=1):
        self.client = mph.start(cores=cores) 
        self.cores = cores
        try:
            self.model = self.client.load(model_path)
            self.model_path = model_path
            print("Loaded model on", self.cores, "core(s):", self.client.models())
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
        self.model.build()  # Build the model after setting the parameter

    def save(self, name):
        self.model.save(name)

class ACC_ComsolInterface(ComsolInterface):    
    def get_displacement(self):
        return self.model.evaluate('solid.disp','mm') 
    
    def update(self, solution): # update the model with the solution, specifically the height, thickness and width of the beam
        self.set_parameter('H', solution[0])
        self.set_parameter('Thickn', solution[1])
        self.set_parameter('W', solution[2])
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
        (r,z,stress) = self.model.evaluate(['r','z','solid.mises_peak'])
        if selection == 1:
            mask = self.create_AlN_mask(r,z)
        else:
            mask = self.create_electrode_mask(r,z) # Create the mask for the ALN
        filtered_stress = stress[0:self.frequency_steps][mask]
        FOM = sum(filtered_stress) # sum up the displacement to get the figure of merit in frequency 20Hz to 20kHz
        return FOM

    def get_current_FOM(self,selection=1): # the all current of the ALN layer
        (r,z,current) = self.model.evaluate(['r','z','es.normJ']) # return unit is A/m^2
        current_non_nan = np.nan_to_num(current, nan=0.0) # replace the nan with 0 since the current in some postion can't be correctly measured
        if selection == 1: 
            mask = self.create_AlN_mask(r,z) # Create the mask for the ALN
        else: 
            mask = self.create_electrode_mask(r,z)
        filtered_current = current_non_nan[0:self.frequency_steps][mask]
        FOM = sum(filtered_current) # sum up the current to get the figure of merit in frequency 20Hz to 20kHz
        return FOM
    
    def get_charge_FOM(self,selection=1): # es.nD is not working here I use normD instead
        (r,z,charge) = self.model.evaluate(['r','z','es.normD'])
        charge_non_nan = np.nan_to_num(charge, nan=0.0) # replace the nan with 0 since the charge in some postion can't be correctly measured
        if selection == 1:
            mask = self.create_AlN_mask(r,z) # Create the mask for the ALN
        else:
            mask = self.create_electrode_mask(r,z) # Create the mask for the electrode
        filtered_charge = charge_non_nan[0:self.frequency_steps][mask]
        FOM = sum(filtered_charge)  
        return FOM

    def update(self, solution): # store the values of the solution and update the model with the solution
        self.t_silicon, self.radius, self.t_AlN, self.t_SiO2, r_electrode_factor = solution
        self.r_electrode = r_electrode_factor * self.radius # r_electrode is the inner circle of the electrode 
        self.set_parameter('t_silicon',f'{self.t_silicon}[um]')
        self.set_parameter('radius',f'{self.radius}[um]')
        self.set_parameter('t_AlN',f'{self.t_AlN}[um]')
        self.set_parameter('t_SiO2',f'{self.t_SiO2}[um]')
        self.set_parameter('r_electrode',f'{(self.r_electrode)}[um]')
        return self.model
    
    class Speaker_3D_ComsolInterface(ComsolInterface):
        frequency_steps = 40 # the simluation step size is 500Hz, so the frequency range is from 20Hz to 20kHz

        def update(self, solution): # store the values of the solution and update the model with the solution
            self.t_silicon = solution[0]

        # def get_stress_FOM(self):
            # x_min, x_max = 
            # y_min, y_max =
            # z_min, z_max =
            # mask = (x[0:self.frequency_steps] >= x_min) & (x[0:self.frequency_steps] <= x_max) & (y[0:self.frequency_steps] >= y_min) & (y[0:self.frequency_steps] <= y_max) & (z[0:self.frequency_steps] >= z_min) & (z[0:self.frequency_steps] <= z_max)
            
# test code for the data read and set functions
if __name__ == '__main__':
    model = Speaker_2D_ComsolInterface('2D_Piezoelectric_Microphone_for_GA_based_Optimization.mph',cores=24)
    solution = [14, 6400, 0.7, 1.3, 0.4]
    model.update(solution)
    model.run_simulation()
    print(model.model.parameters()) # print the parameters of the model
    print(model.get_stress_FOM())
