"""
Defactorise.py - Assignment Variable Extraction Utilities

This module provides utility functions to extract and decode assignment variables
from the optimization model solutions. It handles both static and time-extended models.

Key Functions:
- XAsignmentsDefactorise: Extract task assignments (static model)
- ZAsignmentsDefactorise: Extract depot assignments (static model)
- TEXAsignmentsDefactorise: Extract task assignments (time-extended model)
- TEZAsignmentsDefactorise: Extract depot assignments (time-extended model)
- TInfo: Extract battery level variables (time-extended model)

Variable Naming Convention:
- x_i_k_v: Implement i with vehicle v performs task k (static)
- x_i_k_v_t: Implement i with vehicle v performs task k in period t (time-extended)
- z_v: Vehicle v returns to depot (static)
- z_v_t: Vehicle v returns to depot in period t (time-extended)
- T_v_t: Battery level of vehicle v at period t (time-extended)

Author: Jorge
Date: 2024
"""

import numpy as np

def XAsignmentsDefactorise(Asignments):
    """
    Extract task assignment indices for static model.
    
    Parses variable names like "x_2_5_1" (implement 2, task 5, vehicle 1)
    and extracts the indices.
    
    Args:
        Asignments (dict): Dictionary of assignment variables {name: value}
                          Only variables with value > 0 should be passed
    
    Returns:
        tuple: (A_implements, A_tasks, A_vehicles)
            Three lists containing the indices for each assignment
    """
    A_implements = []
    A_tasks = []
    A_vehicles = []
    if Asignments:
        for key, value in Asignments.items():
            _, i, j, k = key.split('_')
            A_implements.append(int(i))
            A_tasks.append(int(j))
            A_vehicles.append(int(k))

    return A_implements, A_tasks, A_vehicles

def ZAsignmentsDefactorise(Asignments):
    """
    Extract depot assignment indices for static model.
    
    Parses variable names like "z_3" (vehicle 3 at depot).
    
    Args:
        Asignments (dict): Dictionary of depot assignment variables {name: value}
    
    Returns:
        list: A_vehiclesd - List of vehicle indices that are at depot
    """
    A_vehiclesd = []
    if Asignments:
        for key, value in Asignments.items():
            _, i = key.split('_')
            A_vehiclesd.append(int(i))

    return A_vehiclesd

def TEXAsignmentsDefactorise(Asignments):
    """
    Extract task assignment indices for time-extended model.
    
    Parses variable names like "x_2_5_1_0" (implement 2, task 5, vehicle 1, period 0).
    
    Args:
        Asignments (dict): Dictionary of assignment variables {name: value}
    
    Returns:
        tuple: (A_implements, A_tasks, A_vehicles, A_periods)
            Four lists containing the indices for each assignment including time period
    """
    A_implements = []
    A_tasks = []
    A_vehicles = []
    A_periods = []
    if Asignments:
        for key, value in Asignments.items():
            _, i, j, k ,t= key.split('_')
            A_implements.append(int(i))
            A_tasks.append(int(j))
            A_vehicles.append(int(k))
            A_periods.append(int(t))

    return A_implements, A_tasks, A_vehicles, A_periods

def TEZAsignmentsDefactorise(Asignments):
    """
    Extract depot assignment indices for time-extended model.
    
    Parses variable names like "z_3_1" (vehicle 3 at depot in period 1).
    
    Args:
        Asignments (dict): Dictionary of depot assignment variables {name: value}
    
    Returns:
        tuple: (A_vehiclesd, A_periodsD)
            - A_vehiclesd: List of vehicle indices at depot
            - A_periodsD: List of corresponding time periods
    """
    A_vehiclesd = []
    A_periodsD = []
    if Asignments:
        for key, value in Asignments.items():
            _, i, t = key.split('_')
            A_vehiclesd.append(int(i))
            A_periodsD.append(int(t))

    return A_vehiclesd, A_periodsD

def TInfo(Asignments,num_vehicles,num_periods):
    """
    Extract battery level information for time-extended model.
    
    Parses continuous variables like "T_2_1" (battery of vehicle 2 at period 1).
    Constructs a matrix of battery levels across all vehicles and periods.
    
    Args:
        Asignments (dict): Dictionary of battery variables {name: value}
        num_vehicles (int): Number of vehicles
        num_periods (int): Number of time periods
    
    Returns:
        np.array: Tinfo matrix [num_vehicles x num_periods]
            Tinfo[v, t] = battery level of vehicle v at start of period t
    """
    Tinfo=np.zeros((num_vehicles,num_periods))
    if Asignments:
        for clave, valor in Asignments.items():
            partes = clave.split('_')
            i = int(partes[1])
            j = int(partes[2])
            Tinfo[i, j] =int(valor)

    return Tinfo





