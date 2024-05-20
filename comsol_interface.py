import mph

class ACC_ComsolInterface:
    def __init__(self, model_path):
        self.client = mph.start(cores=1) # Start the COMSOL client
        try:
            self.model = self.client.load(model_path)
            self.model_path = model_path
            print("Loaded model on one core:",self.client.models())
        except Exception as e:
            print("Error: Could not load the model.",e)
            exit()

    def run_simulation(self):
        self.model.mesh() # Mesh the geometry
        self.model.solve() # normally there is only one study
        return self.model

    def clear(self):
        self.model.clear() # Clear disk space for history and results
    
    def get_displacement(self):
        return self.model.evaluate('solid.disp','mm') 
    
    def set_parameter(self, name, value):
        self.model.parameter(name=name, value=value) # Set the parameter of the model, name is the name of the parameter, value is the value of the parameter
        self.model.build()  # Build the model after setting the parameter
        return self.model
    
    def update(self, solution): # update the model with the solution, specifically the height, thickness and width of the beam
        self.set_parameter('H', solution[0])
        self.set_parameter('Thickn', solution[1])
        self.set_parameter('W', solution[2])
        return self.model
    
class Speaker_2D_ComsolInterface:
    frequency_steps = 40 # the number of frequency steps in the simulation. Change if the model study steps is changed

    def __init__(self, model_path):
        self.client = mph.start(cores=1) # Start the COMSOL client
        try:
            self.model = self.client.load(model_path)
            self.model_path = model_path
        except Exception as e:
            print("Error: Could not load the model.",e)
            exit()

    def run_simulation(self):
        self.model.mesh() # Mesh the geometry
        self.model.solve() # normally there is only one study
        return self.model

    def clear(self):
        self.model.clear() # Clear disk space for history and results
    
    def get_disp_FOM(self):
        displacement = self.model.evaluate('solid.disp','mm') # as we know the frequency simulation range is from 100Hz to 80kHz with step size of 500Hz, so we can have a FOM from 20Hz to 20kHz
        FOM = sum(displacement[0:self.frequency_steps][:,0]) # select displacement from 20Hz to 20kHz, and sum them up as integral, first column is the spatial coordinator at (0,0,0) 
        return FOM

    def set_parameter(self, name, value):
        self.model.parameter(name=name, value=value) # Set the parameter of the model, name is the name of the parameter, value is the value of the parameter
        self.model.build()  # Build the model after setting the parameter
        return self.model
    
    def get_current_FOM(self, solution): # the current of the ALN
        r_min, r_max = 0, solution[1]*solution[4] # calculate the min and max radius of the ALN
        z_min, z_max = solution[0] + solution[3], solution[0] + solution[2] + solution[3] # calculate the min and max height of the piezoelectric material
        [r,z,current] = self.model.evaluate(['r','z','es.normJ']) # here it return the A/m^2 all across the surface, choose the surface on pizeoelectric material to get the charge
        mask = [(r[0:self.frequency_steps] >= r_min) & (r[0:self.frequency_steps] <= r_max) & (z[0:self.frequency_steps] >= z_min) & (z[0:self.frequency_steps] <= z_max)]
        filtered_current = current[0:self.frequency_steps][mask[0]]
        FOM = sum(filtered_current) # sum up the current to get the figure of merit in frequency 20Hz to 20kHz
        return FOM
    
    def update(self, solution): # update the model with the solution, specifically the height, thickness and width of the beam
        self.set_parameter('t_silicon',f'{solution[0]}[um]')
        self.set_parameter('radius',f'{solution[1]}[um]')
        self.set_parameter('t_AlN',f'{solution[2]}[um]')
        self.set_parameter('t_SiO2',f'{solution[3]}[um]')
        self.set_parameter('r_electrode',f'{(solution[4]*solution[1])}[um]')
        return self.model
    
# test code for the data read and set functions
if __name__ == '__main__':
    model = Speaker_2D_ComsolInterface('2D_Piezoelectric_Microphone_for_GA_based_Optimization.mph')
    solution = [10, 1000, 0.6, 0.5, 0.8]
    model.run_simulation()
    model.update(solution)
    print(model.model.parameters()) # print the parameters of the model
    print(model.get_current_FOM(solution))
