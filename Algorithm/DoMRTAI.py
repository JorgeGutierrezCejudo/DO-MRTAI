"""
DoMRTAI.py - Dynamic Multi-Robot Task Assignment with Implements Algorithm

This module implements the core optimization algorithm for the D-MRTAI system.
It handles the dynamic assignment of tasks to robot-implement pairs, considering:
- Multi-period planning horizons
- Dynamic events (task/vehicle/implement appearance/disappearance)
- Battery/energy constraints
- Compatibility constraints between robots, implements, and tasks
- Cost minimization objectives

The algorithm uses Mixed Integer Programming (MIP) via Gurobi solver and integrates
with a real-time simulation/visualization system.

Key Components:
- Cost calculations (static and dynamic)
- Compatibility matrix management
- Event-driven re-optimization
- Real-time visualization and movement simulation
- Post-processing and results tracking

Author: Jorge
Date: 2024
"""

# Standard library imports
import os
import json
import time
import math

# Third-party library imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate
from gurobipy import GRB
import roslibpy

# Project-specific imports
from Data import Cost as ct
from Data import Data as dt
from Processing import Preprocessing as pp
from Processing import PostProcessing as pop
from View import Movement as mv
from Models import StaticModelSMC as sm
from Models import TimeExtendModelSMC as dm
from Events import EventLogger as EVlogger
from Events import Events as EV


def init(Implements, Tasks, Vehicles, T, num_periods, probabilityTA, probabilityTD, probabilityVA, probabilityVD, probabilityID, probabilityIA, full, set_data):
    """
    Initialize and run the D-MRTAI optimization algorithm.
    
    This is the main entry point for the optimization system. It manages the complete
    simulation lifecycle including initialization, optimization loop, event handling,
    visualization, and post-processing.
    
    Args:
        Implements (np.array): Matrix of implement data [x, y, efficiency, state]
        Tasks (np.array): Matrix of task data [x, y, area, penalty, state]
        Vehicles (np.array): Matrix of vehicle data [x, y, efficiency, T_max, T_current, state]
        T (int): Time horizon for the simulation
        num_periods (int): Number of planning periods (1 for static, >1 for time-extended)
        probabilityTA (float): Probability of task appearance event
        probabilityTD (float): Probability of task disappearance event
        probabilityVA (float): Probability of vehicle appearance event
        probabilityVD (float): Probability of vehicle disappearance event
        probabilityID (float): Probability of implement disappearance event
        probabilityIA (float): Probability of implement appearance event
        full (bool): Use full compatibility matrices (True) or load/generate sparse (False)
        set_data (int): Random seed for data generation
        
    Returns:
        tuple: (t, toptimization, Obj, DoneAsignationCost, StaticCostTask, Distancia_list, RobotPerformanceList)
            - t: Total elapsed simulation time
            - toptimization: Total time spent on optimization
            - Obj: Final objective function value
            - DoneAsignationCost: Cost of completed task assignments
            - StaticCostTask: Static cost component
            - Distancia_list: List of distances traveled by each vehicle
            - RobotPerformanceList: Performance metrics for each robot
    """
    # ==========================
    # 1. Environment Variables
    # ==========================
    DATA_FILE = "View/simulation_data.json"  # JSON file for visualization data
    
    # Tracking variables for completed assignments and tasks
    InfoTaskDone = []      # List of completed tasks with timing info
    AssigmentDone = []     # List of all assignments made during simulation
    
    # Simulation state variables
    data = 1
    t = 0                  # Current simulation time
    toptimization = 0      # Cumulative optimization time
    Obj = 0                # Objective function value
    CostPenaltyRest = 0    # Remaining penalty costs
    DoneAsignationCost = 0 # Cost of completed assignments
    CostDistance = 0       # Total distance cost
    
    # Event management: [is_event, event_type, event_data]
    Event = [True, "", 0]
    
    # Solution variables from optimization model
    XAsignments = {}  # Task assignments: x[i,k,v] or x[i,k,v,t]
    ZAsignments = {}  # Depot assignments: z[v] or z[v,t]
    TAsignments = {}  # Battery levels: T[v,t] (time-extended only)

    # Optimization parameters
    b = 0  # Energy consumption matrix
    totalDistancia = np.ones((len(Vehicles)), dtype=float)  # Cumulative distance per vehicle
    Distancia = np.ones((len(Vehicles)), dtype=float)       # Current period distance per vehicle
    
    # Weight parameters for cost functions
    CostBalance = [0, 1]     # [Static weight, Dynamic weight]
    alpha, beta = 0.05, 0.95 # Objective function weights: cost vs penalty
    EnergyBalance = [0, 1]   # [Static weight, Dynamic weight] for energy
    Tmin = 0                 # Minimum battery level threshold

    # Directory and event logging
    dir = os.getcwd()
    EventLogger = EVlogger.EventLogger()  # Centralized event logging system

    # ==========================
    # 2. Main Simulation Loop
    # ==========================
    # Continue while there are tasks to complete and within time horizon
    while (len(Tasks) > 0) and (t < T):
        if Event[0]:  # An event has occurred, need to re-optimize
            Obj_prime = 0
            Event[0] = False
            
        # ==========================
        # 2.1 Preprocessing - Prepare data for optimization
        # ==========================
            # ==========================
            # 2.1.1 Update States
            # Extract current state of all entities
            # ==========================
            StImplement = Implements[:, 3]  # State vector for implements
            StTask = Tasks[:, 4]            # State vector for tasks (0=available, 1=completed)
            StVehicle = Vehicles[:, 5]      # State vector for vehicles

            # Count active entities
            num_implements = len(Implements)
            num_tasks = len(Tasks)
            num_vehicles = len(Vehicles)

            # ==========================
            # 2.1.2 Dynamic Variables - Time-extended model parameters
            # ==========================
            # Availability matrices: indicate which entities are available in each period
            Vhat = np.ones((num_periods, num_vehicles)).astype(int)   # Vehicle availability
            Ihat = np.ones((num_periods, num_implements)).astype(int) # Implement availability
            Khat = np.ones((num_periods, num_tasks), dtype=int).astype(int)  # Task availability
            Khat[1:num_periods][:] = 0  # Tasks only available in first period initially

            # Penalty calculation: increases cubically with time to encourage early completion
            if t==0: 
                M = Tasks[:, 3]  # Initial penalty from task data
            else: 
                M = (0.2*t*t*t) + Tasks[:, 3]  # Time-dependent penalty increase

            # Battery/energy parameters
            That = Vehicles[:, 4]    # Current battery level for each vehicle
            T_max = Vehicles[:, 3]   # Maximum battery capacity for each vehicle

            # Active entity sets (only entities with state=0 are available)
            I = [i for i, State in enumerate(StImplement) if State == 0]  # Available implements
            K = [k for k, State in enumerate(StTask) if State == 0]       # Available tasks
            V = [i for i, State in enumerate(StVehicle) if State == 0]    # Available vehicles
            Tau = range(num_periods)  # Time period indices

            # ==========================
            # 2.1.3 Cost and Energy Calculations
            # Calculate both static (task-based) and dynamic (distance-based) costs
            # ==========================
            # Dynamic cost: based on Euclidean distances between entities
            Cd, Bd = ct.DynamicCalculation(num_implements, num_tasks, num_vehicles, Implements, Tasks, Vehicles)
            
            # Static cost: based on task area and entity efficiencies
            Cst, Bst = ct.StaticCalculation(num_implements, num_tasks, num_vehicles, Implements, Tasks, Vehicles)
            
            # Depot return cost for each vehicle
            Cprime = ct.PrimeCalculation(num_implements, num_tasks, num_vehicles, Implements, Tasks, Vehicles)

            # For time-extended models, replicate costs across all periods with variations
            if num_periods > 1:
                Cst, Cd, Bst, Bd, M, Cprime = ct.TimeExtendCalculation(
                    num_periods, num_implements, num_tasks, num_vehicles, Cst, Cd, Bst, Bd, M, Cprime, Tasks
                )
            
            # Combined energy consumption matrix (weighted sum of static and dynamic)
            b = (EnergyBalance[0] * Bst + EnergyBalance[1] * Bd).astype(int)

            # ==========================
            # 2.1.4 Compatibility Data
            # Load or generate compatibility matrices between implements, tasks, and vehicles
            # ==========================
            os.chdir(dir)
            IK, KI, IV, VI, KV, VK = dt.CompatibilityData(num_implements, num_tasks, num_vehicles, full, set_data)
            os.chdir(dir)

        # ==========================
        # 2.2 Optimization Model
        # Solve the Mixed Integer Programming problem
        # ==========================
            Error = 10  # Error threshold for ROS integration (if enabled)
            while Error > 5:
                # Combine static and dynamic costs using configured weights
                C = (CostBalance[0] * Cst + CostBalance[1] * Cd).astype(int)
                
                # Normalize costs and penalties for numerical stability
                Cmax, Mmax = ct.NormalicedCalculation(num_periods, M, I, K, V, C, Cprime)

                # Select optimization model based on planning horizon
                if num_periods <= 1:
                    # Static model: single period optimization
                    modelo = sm.Optimization(C, M, That, I, K, V, Mmax, Cmax, IK, KI, IV, VI, KV, VK, alpha, beta, b, Cprime, Tmin)
                else:
                    # Time-extended model: multi-period optimization with battery dynamics
                    modelo = dm.Optimization(
                        C, M, That, I, K, V, Mmax, Cmax, IK, KI, IV, VI, KV, VK, alpha, beta, T_max, b, Tau, Vhat, Ihat, Khat, Cprime, Tmin
                    )

                os.chdir(dir)

                # Handle infeasible models (no feasible solution exists)
                if modelo.Status == GRB.Status.INFEASIBLE:
                    print("The model is infeasible. Stopping optimization.")
                    modelo.write("infeasible_model.ilp")  # Save model for debugging
                    break

                # ==========================
                # Extract solution variables from the optimization model
                # Handles both Gurobi and SCIP solvers
                # ==========================
                try:
                    # Gurobi solver solution extraction
                    all_vars = modelo.getVars()
                    tprime = modelo.getAttr("Runtime")  # Optimization solve time
                    values = modelo.getAttr("X", all_vars)  # Variable values
                    names = modelo.getAttr("VarName", all_vars)  # Variable names
                    
                    # Extract task assignments: x[i,k,v] or x[i,k,v,t]
                    XAsignments = {name: val for name, val in zip(names, values) if (val > 0 and name.startswith('x'))}
                    
                    # Extract depot assignments: z[v] or z[v,t]
                    ZAsignments = {name: val for name, val in zip(names, values) if (val > 0 and name.startswith('z'))}
                    
                    # Extract battery levels for time-extended model: T[v,t]
                    if num_periods > 1:
                        TAsignments = {name: val for name, val in zip(names, values) if (val > 0 and name.startswith('T'))}
                except:
                    # SCIP solver solution extraction (alternative solver)
                    XAsignments = {}
                    ZAsignments = {}
                    tprime = modelo.getSolvingTime()
                    solution = modelo.getBestSol()
                    all_vars = modelo.getVars()
                    for var in all_vars:
                        val = modelo.getSolVal(solution, var)
                        name = var.name
                        if val > 0:
                            if name.startswith('x'):
                                XAsignments[name] = val
                            elif name.startswith('z'):
                                ZAsignments[name] = val

                Error = 0
                # Error, Cd = rc.RealCost(XAsignments, Implements, Tasks, Vehicles, Cd, client)

        # ==========================
        # 2.3 Visualization of the Solution (Optional)
        # ==========================
            # if num_periods <= 1:
            #     vw.init(num_implements, num_tasks, num_vehicles, Implements, Tasks, Vehicles, XAsignments, M, That, ZAsignments)
            # else:
            #     tew.init(num_implements, num_tasks, num_vehicles, Implements, Tasks, Vehicles, XAsignments, M, num_periods, ZAsignments, TAsignments)

            os.chdir(dir)
            toptimization = toptimization + tprime

        # ==========================
        # 2.3 Animation and Movement Simulation
        # Execute the assigned routes and visualize vehicle movements
        # ==========================
        if Event[0]==False: 
            # Run animated simulation of vehicle movements
            # Returns: events, updated positions, completed assignments, timing, distances
            Event,Vehicles,Implements,Tasks,AssignmentT,depot_info,tmo,Distancia,totalDistancia=mv.custom_animation(
                Implements, Tasks, Vehicles, XAsignments, ZAsignments, probabilityTA, probabilityTD, 
                probabilityVA, probabilityVD, probabilityID, probabilityIA, 0, totalDistancia, num_periods
            )
        
        # ==========================
        # 2.4 Post-Processing - Update system state after movements
        # ==========================
        if Event[0]:  # Process completed assignments and events
            # Convert completed movements to assignment format and update tracking
            XAsignments,InfoTaskDone,ZAsignments=pop.AssignmentDone(AssignmentT,t,InfoTaskDone,M,depot_info) 
            
            # Update system state based on completed assignments
            try:
                # Static model update: simple state transitions
                Implements,Tasks,Vehicles,M,That=pp.UpdateInfoST(XAsignments,Implements,Tasks,Vehicles,M,That,b,ZAsignments,T_max,Distancia)
            except:
                # Time-extended model update: complex battery dynamics
                Implements,Tasks,Vehicles,M,That=pp.UpdateInfoTE(XAsignments,Implements,Tasks,Vehicles,M,That,num_periods,ZAsignments,b,T_max,TAsignments,num_vehicles)

            # ==========================
            # 2.4.1 Update Assignment Tracking Lists
            # ==========================
        if XAsignments is not None:
            # Append new assignments to history
            AssigmentDone.append(XAsignments)
            # Organize assignments by robot for performance analysis
            AssigmentDoneList=pop.AssignmentByRobot(AssigmentDone)
            
        # Update simulation time
        t=t+(tmo)


            # ==========================
            # 2.4.2 Event Processing
            # ==========================

        if Event[0]:  
            # Process different types of events and trigger re-optimization
            if Event[1]=="Task":
                # New task appeared or task disappeared
                EventProcess = EV.TaskEvent("Task event", Event[2],1)
                NTasks = EventProcess.process()
                Tasks=np.concatenate((Tasks,NTasks),axis=0)  # Add new tasks to list
                EventLogger.log_event(EventProcess)
               
            elif Event[1]== "Vehicle" :
                # New vehicle appeared or vehicle broke down
                EventProcess = EV.VehicleEvent("New Vehicle", Event[2],Vehicles,1,data)
                Vehicles = EventProcess.process()  # Update vehicle list
                EventLogger.log_event(EventProcess)
                
            elif Event[1]=="Implement":
                # New implement appeared or implement disappeared
                EventProcess = EV.ImplementEvent("New Implement", Event[1],1)
                NImplements =EventProcess.process()
                EventLogger.log_event(EventProcess)
                
            elif Event[1]=="Simulation":
                # Simulation events: task completion or battery recharge
                if Event[2]==2:
                    # Battery recharge event
                    SimulationData = [ZAsignments,That,T_max]
                else:
                    # Task completion event
                    SimulationData = []
                EventProcess = EV.SimulationEvent("Simulation Event", Event[2],SimulationData) 
                SimulationOutput=EventProcess.process()
                EventLogger.log_event(EventProcess)
                
                if Event[2]==2:
                    # Update battery levels after recharge
                    That=SimulationOutput[0]
                    Vehicles[:,4]=That
                    T_max=SimulationOutput[1]
            else:
                print("Error: EVENT NOT FOUND")

        # Get total event count for reporting
        Info=EventLogger.get_events_by_type()
        Info=len(Info)

        # ==========================
        # 2.5 Real-time Visualization Data Update
        # Prepare summary statistics for the visualization window
        # ==========================
        
        # Build robot performance list (tasks completed per robot)
        try:
            RobotPerformanceList=[[f"Task done by Robot {i}",AssigmentDoneList[i]["TaskCount"]] for i in AssigmentDoneList.keys()]
        except:
            try: 
                RobotPerformanceList=RobotPerformanceList
            except:
                RobotPerformanceList=[]

        # Prepare summary statistics for display
        That_list = [[f"Battery of vehicule {i}", int(That[i])] for i in range(num_vehicles)]
        Distancia_list = [[f"Distance of vehicule {i}", round(totalDistancia[i],2)] for i in range(num_vehicles)]
        
        summary_data = [
            *That_list,            # Battery levels for all vehicles
            *Distancia_list,       # Distances traveled by all vehicles
            *RobotPerformanceList, # Task completion counts per robot
            ["Total distance", round(sum(totalDistancia), 2)],
            ["Elapsed time", round(t,3)],
            ["Elapsed time of optimization", round(toptimization,5)],
            ["Number of events",Info]
        ]

        # Write summary data to JSON file for real-time visualization
        with open(DATA_FILE, "w") as file:
            json.dump(summary_data, file, indent=4)


        K=[k for k, State in enumerate(StTask) if State == 0]
        if len(K)==0:
            aTasck=Tasks[:,2]
            EfImplement=Implements[:,2]
            EfVehicle=Vehicles[:,2]
            Tasks=[]
        
        if t>T:
            aTasck=Tasks[:,2]
            EfImplement=Implements[:,2]
            EfVehicle=Vehicles[:,2]


    

    
    # ==========================
    # 3. Final Objective Function Calculation
    # Calculate true costs based on actual execution (not just optimization estimates)
    # ==========================
    CostDistance,DoneAsignationCost,StaticCostTask=pop.TrueObj(
        totalDistancia, InfoTaskDone, AssigmentDoneList, EfVehicle, aTasck, EfImplement
    )
    
    # Total objective: sum of all cost components
    Obj = CostDistance + DoneAsignationCost + StaticCostTask
    
    # Return final results
    return t,toptimization,Obj,DoneAsignationCost,StaticCostTask,Distancia_list,RobotPerformanceList



# init(Implements,Tasks,Vehicles,T)
