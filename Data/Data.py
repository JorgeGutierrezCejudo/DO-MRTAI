"""
Data.py - Data Management for D-MRTAI System

This module handles the generation, loading, and management of compatibility and position data
for implements, tasks, and vehicles in the D-MRTAI system.

Key Functions:
- CalculateCompMatrices: Derive all compatibility matrices from IK and IV
- CompatibilityData: Load or generate compatibility matrices between entities
- PositionData: Load or generate 2D position and parameter data for all entities

Data Files Structure:
- Compatibility data: Data/Compatibility/Compatibility-(I,K,V)/
  Contains: IK.csv (Implement-Task), IV.csv (Implement-Vehicle), VK.csv (Vehicle-Task)
  
- Position data: Data/Positions/Positions-(I,K,V)-seed/
  Contains: Implements.csv, Tasks.csv, Vehicles.csv

Author: Jorge
Date: 2024
"""

import numpy as np
import pandas as pd
import os

def CalculateCompMatrices (IK,IV):
    """
    Calculate all compatibility matrices from implement-task and implement-vehicle compatibility.
    
    The compatibility between vehicles and tasks is derived through implements:
    A vehicle can perform a task if there exists an implement compatible with both.
    
    Args:
        IK (np.array): Implement-Task compatibility matrix [num_implements x num_tasks]
                       IK[i,k]=1 if implement i can perform task k
        IV (np.array): Implement-Vehicle compatibility matrix [num_implements x num_vehicles]
                       IV[i,v]=1 if vehicle v can use implement i
    
    Returns:
        tuple: (VK, KV, VI, KI) - All derived compatibility matrices
            - VK: Vehicle-Task compatibility [num_vehicles x num_tasks]
            - KV: Task-Vehicle compatibility (transpose of VK)
            - VI: Vehicle-Implement compatibility (transpose of IV)
            - KI: Task-Implement compatibility (transpose of IK)
    """
    # Calculate VK (compatibility between vehicle and task)
    # Matrix multiplication: if any implement can bridge vehicle to task, they're compatible
    VK = (np.dot(IV.T, IK) > 0).astype(int)

    # Calculate transposes for different indexing needs
    KV = VK.T  # Task-Vehicle compatibility
    KI = IK.T  # Task-Implement compatibility
    VI = IV.T  # Vehicle-Implement compatibility

    return VK,KV,VI,KI
    
    

def CompatibilityData(num_implements,num_tasks,num_vehicles,full,set_data):
    """
    Load or generate compatibility matrices between implements, tasks, and vehicles.
    
    This function either:
    1. Returns full compatibility (all 1s) if full=True
    2. Loads existing compatibility data from files
    3. Generates new random compatibility data and saves it
    
    Args:
        num_implements (int): Number of implements in the system
        num_tasks (int): Number of tasks in the system
        num_vehicles (int): Number of vehicles in the system
        full (bool): If True, return full compatibility matrices (all combinations allowed)
        set_data (int): Random seed for reproducible generation
    
    Returns:
        tuple: (IK, KI, IV, VI, KV, VK) - All compatibility matrices
            Allows efficient lookup regardless of indexing order needed
    """
    os.chdir("Data/Compatibility/")
    directory_path="Compatibility-("+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+")"
    
    if full==True:
        # Full compatibility mode: all entities can work with all others
        IV = np.ones((num_implements, num_vehicles)) 
        IK = np.ones((num_implements, num_tasks)) 
        VK,KV,VI,KI=CalculateCompMatrices(IK,IV)

    else:
        # Partial compatibility mode: load or generate sparse matrices
        if os.path.exists(directory_path):
            # Load existing compatibility data
            os.chdir(directory_path)
            IK=np.loadtxt('IK.csv', delimiter=',', dtype=int)
            IV =np.loadtxt('IV.csv', delimiter=',', dtype=int)        
            VK,KV,VI,KI=CalculateCompMatrices(IK,IV)

        else:
            # Generate new random compatibility data
            np.random.seed(set_data)
            IK = np.random.randint(0, 2, size=(num_implements, num_tasks))  # Random 0/1 matrix
            IV = np.random.randint(1, 2, size=(num_implements, num_vehicles))  # All 1s (vehicles can use all implements)
            
            # Create directory and save data
            os.makedirs(directory_path)
            os.chdir(directory_path)
            VK,KV,VI,KI=CalculateCompMatrices(IK,IV)
            pd.DataFrame(IK).to_csv('IK.csv', index=False, header=False)
            pd.DataFrame(IV).to_csv('IV.csv', index=False, header=False)
            pd.DataFrame(VK).to_csv('VK.csv', index=False, header=False)

    return IK,KI,IV,VI,KV,VK

def PositionData(num_implements,num_tasks,num_vehicles,set_data):
    """
    Load or generate position and parameter data for all entities.
    
    This function manages the 2D positions and other parameters (efficiency, battery, penalties)
    for implements, tasks, and vehicles. Data is either loaded from existing files or generated
    and saved for future use.
    
    Args:
        num_implements (int): Number of implements to generate/load
        num_tasks (int): Number of tasks to generate/load
        num_vehicles (int): Number of vehicles to generate/load
        set_data (int): Random seed for reproducible generation
    
    Returns:
        tuple: (Implements, Tasks, Vehicles)
            - Implements: [num_implements x 4] - [x, y, efficiency, state]
            - Tasks: [num_tasks x 5] - [x, y, area, penalty, state]
            - Vehicles: [num_vehicles x 6] - [x, y, efficiency, T_max, T_current, state]
            
    State encoding: 0=available, 1=unavailable/completed
    """

    os.chdir("Data/Positions/")
    directory_path="Positions-("+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+")-"+str(set_data)
    
    if os.path.exists(directory_path):
        # Load existing position data
        os.chdir(directory_path)
        print("Data Exists")
        Implements = np.loadtxt('Implements.csv', delimiter=',',dtype=float).reshape(num_implements,4)
        Tasks = np.loadtxt('Tasks.csv', delimiter=',', dtype=float).reshape(num_tasks,5)
        Vehicles = np.loadtxt('Vehicles.csv', delimiter=',', dtype=float).reshape(num_vehicles,6)
    else:
        # Generate new position data
        os.makedirs(directory_path)
        os.chdir(directory_path)
        print("Data not Exist")
        
        # Generate Implements: [x, y, efficiency, state]
        np.random.seed(set_data)
        Implements = np.random.randint(0, 100, size=(num_implements,2))  # x, y positions
        np.random.seed(set_data)
        EfImplement=  np.random.randint(80, 100, size=(num_implements,1))  # Efficiency 80-100%
        StImplement=np.zeros((num_implements))  # All available initially
        Implements = np.concatenate((Implements,EfImplement/100),axis=1)  # Normalize efficiency to [0.8, 1.0]
        Implements = np.concatenate((Implements,StImplement.reshape(-1,1)),axis=1)
        
        # Generate Tasks: [x, y, area, penalty, state]
        np.random.seed(set_data+10)
        Tasks = np.random.randint(0, 100, size=(num_tasks,3))  # x, y, area
        np.random.seed(set_data+12)
        Penalty=  np.random.randint(100, 1000, size=(num_tasks,1))  # Penalty for not completing
        Tasks = np.concatenate((Tasks,Penalty),axis=1)
        StTask=np.zeros((num_tasks))  # All available initially
        Tasks = np.concatenate((Tasks,StTask.reshape(-1,1)),axis=1)
        
        # Generate Vehicles: [x, y, efficiency, T_max, T_current, state]
        np.random.seed(set_data+20)
        Vehicles = np.random.randint(0, 100, size=(num_vehicles,2))  # x, y positions
        np.random.seed(set_data+20)
        EfVehicle=  np.random.randint(80, 100, size=(num_vehicles,1))  # Efficiency 80-100%
        Vehicles = np.concatenate((Vehicles,EfVehicle/100),axis=1)  # Normalize to [0.8, 1.0]
        
        # Battery parameters
        np.random.seed(set_data)  
        T_max = np.random.randint(100,101, size=(num_vehicles))  # Maximum battery capacity
        Vehicles = np.concatenate((Vehicles,T_max.reshape(-1,1)),axis=1)
        np.random.seed(set_data)  
        That = [np.random.randint(0.75*T_max[i], T_max[i]) for i in range(num_vehicles)]  # Initial battery (75-100% of max)
        That = np.array(That)
        Vehicles = np.concatenate((Vehicles,That.reshape(-1,1)),axis=1)
        StVehicle=np.zeros((num_vehicles))  # All available initially
        Vehicles = np.concatenate((Vehicles,StVehicle.reshape(-1,1)),axis=1)

        # Save generated data to CSV files
        Implements_reshaped = Implements.reshape(-1, 4)
        Tasks_reshaped = Tasks.reshape(-1, 5)
        Vehicles_reshaped = Vehicles.reshape(-1, 6)

        pd.DataFrame(Implements_reshaped).to_csv('Implements.csv', index=False, header=False)
        pd.DataFrame(Tasks_reshaped).to_csv('Tasks.csv', index=False, header=False)
        pd.DataFrame(Vehicles_reshaped).to_csv('Vehicles.csv', index=False, header=False)

    return Implements,Tasks,Vehicles


    
