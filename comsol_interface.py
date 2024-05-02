from bz2 import compress
import mph

class ACC_ComsolInterface:
    def __init__(self, model_path):
        self.client = mph.start(cores=1) # Start the COMSOL client
        try:
            self.model = self.client.load(model_path)
            self.model_path = model_path
            print("Loaded model:",self.client.models())
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
    def __init__(self, model_path):
        self.client = mph.start(cores=1) # Start the COMSOL client
        try:
            self.model = self.client.load(model_path)
            self.model_path = model_path
            print("Loaded model:",self.client.models())
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
        return self.model.evaluate('')
    
    def set_parameter(self, name, value):
        self.model.parameter(name=name, value=value) # Set the parameter of the model, name is the name of the parameter, value is the value of the parameter
        self.model.build()  # Build the model after setting the parameter
        return self.model
    
    def update(self, solution): # update the model with the solution, specifically the height, thickness and width of the beam
        return self.model