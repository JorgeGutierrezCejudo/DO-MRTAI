from datetime import datetime
import numpy as np

class Event:
    def __init__(self, event_type, description, timestamp=None):
        self.event_type = event_type
        self.description = description
        self.timestamp = timestamp if timestamp else datetime.now()

    def __str__(self):
        return (
                    "***************************************************************************************************************\n"
                    f"                   TYPE OF EVENT: {self.event_type}  TIME TRIGGERED: {self.timestamp} \n"
                    "***************************************************************************************************************"
                )

    def process(self):
        pass

class TaskEvent(Event):
    def __init__(self, description, task_id,num, **kwargs):
        super().__init__("Task", description, **kwargs)
        self.task_id = task_id
        self.num = num

    def process(self):
        if self.task_id == 1:
            NTasks = np.random.randint(0, 100, size=(self.num,3))
            Penalty=  np.random.randint(100, 1000, size=(self.num,1))
            NTasks = np.concatenate((NTasks,Penalty),axis=1)
            return NTasks



class VehicleEvent(Event):
    def __init__(self, description, vehicle_id, vehicle_data,num,data, **kwargs):
        super().__init__("Vehicle", description, **kwargs)
        self.vehicle_id = vehicle_id
        self.vehicle_data = vehicle_data  
        self.num=num
        self.data=data

    def process(self):
        Vehicles=self.vehicle_data
        if self.vehicle_id == 2:
                self.description="VEHICLE BROKE"
                print (
                    "***************************************************************************************************************\n"
                    f"                   {self.description} - RE-CALCULATION THE ROUTES\n"
                    "***************************************************************************************************************"
                )
    

            
        elif self.vehicle_id==1:
                self.description="NEW VEHICLE"
                print (
                    "***************************************************************************************************************\n"
                    f"                   {self.description}  - RE-CALCULATION THE ROUTES\n"
                    "***************************************************************************************************************"
                )
                self.data=np.random.randint(1,100)
                np.random.seed(self.data+20)
                Vehicle = np.random.randint(0, 100, size=(self.num,2))
                EfVehicle=  np.random.randint(80, 100, size=(self.num,1))
                Vehicle = np.concatenate((Vehicle,EfVehicle/100),axis=1)
                np.random.seed(self.data+1)  
                T_max = np.random.randint(100,101, size=(self.num)) 
                Vehicle = np.concatenate((Vehicle,T_max.reshape(-1,1)),axis=1)
                np.random.seed(self.data)  
                That = [np.random.randint(0.75*T_max[i], T_max[i]) for i in range(self.num)]
                That = np.array(That)
                Vehicle = np.concatenate((Vehicle,That.reshape(-1,1)),axis=1)
                Vehicles = np.concatenate((Vehicles, Vehicle), axis=0)
        return Vehicles
    
class ImplementEvent(Event):
    def __init__(self, description,Implement_id,Implemet_data, **kwargs):
        super().__init__("Implement", description, **kwargs)
        self.implement_id = Implement_id

    def process(self):
        return print("New Implement")

class SimulationEvent(Event):
    def __init__(self, description,event_id, **kwargs):
        super().__init__("Simulation", description, **kwargs)
        self.event_id = event_id

    def process(self):
        # Lógica específica para eventos generales de simulación
        if self.event_id == 1:
            print (
                    "***************************************************************************************************************\n"
                    f"                   TASK DONE RE-CALCULATION THE ROUTES\n"
                    "***************************************************************************************************************"
                )
        elif self.event_id == 2:
            print (
                    "***************************************************************************************************************\n"
                    f"                   VEHICLE FULL OF BATTERY RE-CALCULATION THE ROUTES\n"
                    "***************************************************************************************************************"
                )
        pass
