"""
Events.py - Event System for Dynamic Simulation

Defines various event types that can occur during the D-MRTAI simulation:
- TaskEvent: New tasks appearing or disappearing
- VehicleEvent: New vehicles appearing or vehicles breaking down
- ImplementEvent: New implements appearing or disappearing
- SimulationEvent: Internal simulation events (task completion, battery recharge)

Each event triggers re-optimization to adapt to the new scenario.

Author: Jorge
Date: 2024
"""

from datetime import datetime
import numpy as np
import Tools.Defactorise as tl


class Event:
    """
    Base class for all simulation events.
    
    Attributes:
        event_type (str): Type of event ("Task", "Vehicle", "Implement", "Simulation")
        description (str): Human-readable description
        timestamp (datetime): When the event occurred
    """
    
    def __init__(self, event_type, description, timestamp=None):
        """Initialize event with type, description, and timestamp."""
        self.event_type = event_type
        self.description = description
        self.timestamp = timestamp if timestamp else datetime.now()

    def __str__(self):
        """Return formatted string representation of event."""
        return (
                    "***************************************************************************************************************\n"
                    f"                   TYPE OF EVENT: {self.event_type}  TIME TRIGGERED: {self.timestamp} \n"
                    "***************************************************************************************************************"
                )

    def process(self):
        """Process event (to be overridden by subclasses)."""
        pass

class TaskEvent(Event):
    """
    Event for task appearance or disappearance.
    
    Attributes:
        task_id (int): Event subtype (1=appearance, 2=disappearance)
        num (int): Number of tasks affected
    """
    
    def __init__(self, description, task_id,num, **kwargs):
        super().__init__("Task", description, **kwargs)
        self.task_id = task_id
        self.num = num

    def process(self):
        """
        Process task event.
        
        For task appearance (task_id=1):
        - Generates new random tasks with positions, areas, and penalties
        - Returns new task matrix to be added to existing tasks
        
        Returns:
            np.array: New tasks matrix [num x 5] (x, y, area, penalty, state)
        """
        if self.task_id == 1:
<<<<<<< Updated upstream
            NTasks = np.random.randint(0, 100, size=(self.num,3))
            Penalty=  np.random.randint(100, 1000, size=(self.num,1))
            NTasks = np.concatenate((NTasks,Penalty),axis=1)
=======
            self.description="NEW TASK APPEARED"
            print (
                    "***************************************************************************************************************\n"
                    f"                   {self.description} - RE-CALCULATION THE ROUTES\n"
                    "***************************************************************************************************************"
            )
            # Generate new tasks: [x, y, area, penalty, state]
            NTasks = np.random.randint(0, 100, size=(self.num,3))  # x, y, area
            Penalty=  np.random.randint(100, 1000, size=(self.num,1))  # Penalty
            NTasks = np.concatenate((NTasks,Penalty),axis=1)
            StTask=np.zeros((self.num))  # All available
            NTasks = np.concatenate((NTasks,StTask.reshape(-1,1)),axis=1)
>>>>>>> Stashed changes
            return NTasks



class VehicleEvent(Event):
    """
    Event for vehicle appearance or breakdown.
    
    Attributes:
        vehicle_id (int): Event subtype (1=appearance, 2=breakdown)
        vehicle_data (np.array): Current vehicle matrix
        num (int): Number of vehicles affected
        data (int): Random seed for generation
    """
    
    def __init__(self, description, vehicle_id, vehicle_data,num,data, **kwargs):
        super().__init__("Vehicle", description, **kwargs)
        self.vehicle_id = vehicle_id
        self.vehicle_data = vehicle_data  
        self.num=num
        self.data=data

    def process(self):
        """
        Process vehicle event.
        
        For vehicle breakdown (vehicle_id=2):
        - Marks vehicle as unavailable (handled externally)
        
        For vehicle appearance (vehicle_id=1):
        - Generates new random vehicle with position, efficiency, battery
        - Appends to existing vehicle matrix
        
        Returns:
            np.array: Updated vehicles matrix
        """
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
                # Generate new vehicle: [x, y, efficiency, T_max, T_current, state]
                self.data=np.random.randint(1,100)
                np.random.seed(self.data+20)
                Vehicle = np.random.randint(0, 100, size=(self.num,2))  # Position
                EfVehicle=  np.random.randint(80, 100, size=(self.num,1))  # Efficiency
                Vehicle = np.concatenate((Vehicle,EfVehicle/100),axis=1)
                np.random.seed(self.data+1)  
                T_max = np.random.randint(100,101, size=(self.num))  # Max battery
                Vehicle = np.concatenate((Vehicle,T_max.reshape(-1,1)),axis=1)
                np.random.seed(self.data)  
                That = [np.random.randint(0.75*T_max[i], T_max[i]) for i in range(self.num)]  # Current battery
                That = np.array(That)
                Vehicle = np.concatenate((Vehicle,That.reshape(-1,1)),axis=1)
                Vehicles = np.concatenate((Vehicles, Vehicle), axis=0)  # Append new vehicle
        return Vehicles
    
class ImplementEvent(Event):
    """
    Event for implement appearance or disappearance.
    
    Attributes:
        implement_id: Event identifier
        Implemet_data: Implement data (unused currently)
    """
    
    def __init__(self, description,Implement_id,Implemet_data, **kwargs):
        super().__init__("Implement", description, **kwargs)
        self.implement_id = Implement_id

    def process(self):
        """Process implement event (placeholder implementation)."""
        return print("New Implement")

class SimulationEvent(Event):
    """
    Event for internal simulation events.
    
    Handles:
    - Task completion (event_id=1): Triggers re-optimization
    - Battery recharge (event_id=2): Restores vehicle batteries to full
    
    Attributes:
        event_id (int): Event subtype (1=task done, 2=recharge)
        SimulationInfo (list): Context data for event processing
    """
    
    def __init__(self, description,event_id,SimulationInfo, **kwargs):
        super().__init__("Simulation", description, **kwargs)
        self.event_id = event_id
        self.SimulationInfo = SimulationInfo

    def process(self):
        """
        Process simulation event.
        
        For task completion (event_id=1):
        - Simply triggers re-optimization
        
        For battery recharge (event_id=2):
        - Restores battery for vehicles that are at depot
        - Returns updated battery levels
        
        Returns:
            list: Updated simulation state (empty for task completion, 
                  [That, Tmax] for battery recharge)
        """
        if self.event_id == 1:
            # Task completion event
            print (
                    "***************************************************************************************************************\n"
                    f"                   TASK DONE RE-CALCULATION THE ROUTES\n"
                    "***************************************************************************************************************"
                )
            SimulationOutput=[]
            return SimulationOutput
        elif self.event_id == 2:
            # Battery recharge event
            print (
                    "***************************************************************************************************************\n"
                    f"                   VEHICLE FULL OF BATTERY RE-CALCULATION THE ROUTES\n"
                    "***************************************************************************************************************"
                )
<<<<<<< Updated upstream
            ZAsignments = self.SimulationInfo[0]
            That = self.SimulationInfo[1]
            Tmax = self.SimulationInfo[2]
            A_vehiclesd =tl.ZAsignmentsDefactorise(ZAsignments)
=======
            ZAsignments = self.SimulationInfo[0]  # Depot assignments
            That = self.SimulationInfo[1]  # Current battery levels
            Tmax = self.SimulationInfo[2]  # Max battery capacities
            
            # Extract which vehicles are at depot
            A_vehiclesd,A_periods=tl.TEZAsignmentsDefactorise(ZAsignments)
            
            # Recharge batteries for vehicles at depot
>>>>>>> Stashed changes
            for i in range(len(A_vehiclesd)):
                That[A_vehiclesd[i]]=Tmax[A_vehiclesd[i]]
            
            SimulationOutput= [That,Tmax]
<<<<<<< Updated upstream
        
            return SimulationOutput
=======
            return SimulationOutput
>>>>>>> Stashed changes
