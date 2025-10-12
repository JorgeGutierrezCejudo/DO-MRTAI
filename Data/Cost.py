"""
Cost.py - Cost and Energy Calculation Functions for D-MRTAI

This module contains all cost and energy consumption calculation functions for the optimization system.
It handles both static costs (based on task characteristics and entity efficiencies) and dynamic costs
(based on Euclidean distances between entities).

Key Functions:
- DynamicCalculation: Distance-based costs and energy consumption
- StaticCalculation: Task-based costs and energy consumption
- PrimeCalculation: Depot return costs for vehicles
- NormalicedCalculation: Normalize costs for numerical stability
- TimeExtendCalculation: Replicate and vary costs across multiple periods

Cost Components:
- Cd: Dynamic cost (distance-based)
- Cst: Static cost (task area / efficiency)
- Cprime: Depot return cost
- Bd: Dynamic energy consumption
- Bst: Static energy consumption

Author: Jorge
Date: 2024
"""

from math import sqrt
import numpy as np

def DynamicCalculation(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles):
    """
    Calculate distance-based costs and energy consumption.
    
    For each (implement, task, vehicle) triple, calculates:
    1. Distance from vehicle to implement
    2. Distance from implement to task
    3. Total distance cost (sum of both)
    4. Energy consumption proportional to distance
    
    Args:
        num_implements, num_tasks, num_vehicles (int): Entity counts
        Implements, Tasks, Vehicles (np.array): Position matrices
    
    Returns:
        tuple: (Cd, Bd) - Dynamic cost and energy matrices [I x K x V]
    """
    xImplement=Implements[:,0]
    yImplement=Implements[:,1]
    xTask=Tasks[:,0]
    yTask=Tasks[:,1]
    xVehicle=Vehicles[:,0]
    yVehicle=Vehicles[:,1]
    Cd=np.zeros((num_implements,num_tasks,num_vehicles))
    Bd=np.zeros((num_implements,num_tasks,num_vehicles))


    for i in range(num_implements):
        for k in range (num_tasks):
            for v in range(num_vehicles):
                Xdiv=abs(xImplement[i]-xVehicle[v])
                Ydiv=abs(yImplement[i]-yVehicle[v])
                Distance1=sqrt(Xdiv**2+Ydiv**2)
                Xdik=abs(xTask[k]-xImplement[i])
                Ydik=abs(yTask[k]-yImplement[i])
                Distance2=sqrt(Xdik**2+Ydik**2)
                Bd[i,k,v]=0.2*((Distance1+Distance2))
                Cd[i,k,v]=Distance1+Distance2
    return Cd,Bd

def StaticCalculation(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles):
    """
    Calculate task-based costs and energy consumption.
    
    Static cost represents the time/effort to complete a task based on:
    - Task area/difficulty (aTasck)
    - Implement efficiency (EfImplement)
    - Vehicle efficiency (EfVehicle)
    
    Formula: Cst[i,k,v] = aTasck[k] / (EfImplement[i] * EfVehicle[v])
    
    Args:
        num_implements, num_tasks, num_vehicles (int): Entity counts
        Implements, Tasks, Vehicles (np.array): Parameter matrices
    
    Returns:
        tuple: (Cst, Bst) - Static cost and energy matrices [I x K x V]
    """
    aTasck=Tasks[:,2]
    EfImplement=Implements[:,2]
    EfVehicle=Vehicles[:,2]
    Cst=np.zeros((num_implements,num_tasks,num_vehicles))
    Bst=np.zeros((num_implements,num_tasks,num_vehicles))

    for i in range(num_implements):
        for k in range (num_tasks):
            for v in range(num_vehicles):
                Cst[i,k,v]=(aTasck[k]/(EfImplement[i]*EfVehicle[v]))
                Bst[i,k,v]=0.2*Cst[i,k,v]
    return Cst,Bst

def PrimeCalculation(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles):
    """
    Calculate depot return costs for all vehicles.
    
    Computes Euclidean distance from each vehicle's current position to depot (origin: 0,0).
    
    Args:
        num_implements, num_tasks, num_vehicles (int): Entity counts
        Implements, Tasks, Vehicles (np.array): Position matrices
    
    Returns:
        np.array: Cprime[v] - Distance from vehicle v to depot [num_vehicles]
    """
    xVehicle=Vehicles[:,0]
    yVehicle=Vehicles[:,1]

    Cprime=np.zeros((num_vehicles))

    for v in range(num_vehicles):
        Xd=abs(xVehicle[v]-0)  # Distance to depot at (0,0)
        Yd=abs(yVehicle[v]-0)
        Distance=sqrt(Xd**2+Yd**2)
        Cprime[v]=Distance
    return Cprime

def NormalicedCalculation(num_periods, M,I,K,V,c_ikv, c_v0_prime):
    """
    Calculate normalization constants for costs and penalties.
    
    Normalizes objective function components to prevent numerical issues
    and balance cost vs penalty terms appropriately.
    
    Args:
        num_periods (int): Number of time periods
        M (np.array): Penalty values
        I, K, V (list): Entity index lists
        c_ikv (np.array): Cost matrix
        c_v0_prime (np.array): Depot return costs
    
    Returns:
        tuple: (Cmax, Mmax) - Normalization constants
            - Cmax: Max cost per vehicle (for cost normalization)
            - Mmax: Total penalty sum (for penalty normalization)
    """

    if num_periods<=1:
        max_cikv=np.zeros(len(V))
        Cmax=np.zeros(len(V))
        for v in V:
            max_cikv[v] = max(c_ikv[i, k, v] for i in I for k in K)
            Cmax[v] = max(max_cikv[v], c_v0_prime[v])

        Mmax = sum(M[k] for k in K)
    else:
        Cmax = 4
        Mmax=sum(M[0][k] for k in K for t in range(num_periods))
                

    return Cmax, Mmax

def TimeExtendCalculation (num_periods,num_implements,num_tasks,num_vehicles,Cst,Cd,bst,bd,M,Cprime,Tasks):
    """
    Extend costs across multiple time periods with variations.
    
    Replicates single-period costs to create multi-period cost matrices,
    adding small random variations to simulate changing conditions over time.
    
    Args:
        num_periods (int): Number of time periods
        num_implements, num_tasks, num_vehicles (int): Entity counts
        Cst, Cd, bst, bd, M, Cprime (np.array): Single-period cost/energy/penalty arrays
        Tasks (np.array): Task information (unused but kept for compatibility)
    
    Returns:
        tuple: (Cst, Cd, bst, bd, M, Cprime) - All extended to [num_periods x ...]
            Each matrix now has time as the first dimension
    """
    
    Cst_pivot=Cst
    Cd_pivot=Cd
    M_pivot=M
    bst_pivot=bst
    Cprime_pivot=Cprime
    bd_pivot=bd

    # Replicate costs for each period with small variations
    for _ in range(num_periods-1):
        Cstt = np.random.normal(loc=Cst, scale=1).astype(int)
        Cst_pivot = np.concatenate((Cst_pivot, Cstt))
        Cdt = np.random.normal(loc=Cd, scale=1).astype(int)
        Cd_pivot = np.concatenate((Cd_pivot, Cdt))
        Mt = np.random.normal(loc=M, scale=1).astype(int)
        M_pivot = np.concatenate((M_pivot, Mt))
        bstt = np.random.normal(loc=bst, scale=1).astype(int)
        bst_pivot = np.concatenate((bst_pivot, bstt))
        bdt = np.random.normal(loc=bd, scale=1).astype(int)
        bd_pivot = np.concatenate((bd_pivot, bdt))
        Cprimet = np.random.normal(loc=Cprime, scale=1).astype(int)
        Cprime_pivot = np.concatenate((Cprime_pivot, Cprimet))
    

    # Reshape to [num_periods x ...]
    Cst=Cst_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)
    Cd=Cd_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)
    Cprime=Cprime_pivot.reshape(num_periods,num_vehicles)
    M=M_pivot.reshape(num_periods,num_tasks)
    bst=bst_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)
    bd=bd_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)

    
    return Cst,Cd,bst,bd,M,Cprime
    
