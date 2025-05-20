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
from View import StView as vw
from View import TEView as tew
from View import Movement as mv
from Models import StaticModelSMC as sm
from Models import DynamicModelSMC as dm
from Events import EventLogger as EVlogger
from Events import Events as EV
from ROS import RealCost as rc


def init(Implements, Tasks, Vehicles, T, num_periods, probabilityTA, probabilityTD, probabilityVA, probabilityVD, probabilityID, probabilityIA, full, set_data):
    # ==========================
    # 1. Environment Variables
    # ==========================
    DATA_FILE = "View/simulation_data.json"
    InfoTaskDone = []
    AssigmentDone = []
    data = 1
    t = 0
    toptimization = 0
    Obj = 0
    CostPenaltyRest = 0
    DoneAsignationCost = 0
    CostDistance = 0
    Event = [True, "", 0]
    XAsignments = {}
    ZAsignments = {}
    TAsignments = {}
    aTasck=Tasks[:,2]
    EfImplement=Implements[:,2]
    EfVehicle=Vehicles[:,2]

    # Optimization variables
    b = 0
    totalDistancia = np.ones((len(Vehicles)), dtype=float)
    Distancia = np.ones((len(Vehicles)), dtype=float)
    CostBalance = [0, 1]
    alpha, beta = 0.05, 0.95
    EnergyBalance = [0, 1]
    Tmin = 0

    # Directory and logger
    dir = os.getcwd()
    EventLogger = EVlogger.EventLogger()

    # ==========================
    # 2. Main Simulation Loop
    # ==========================
    while (len(Tasks) > 0) and (t < T):
        if Event[0]:
            Obj_prime = 0
            Event[0] = False
        # ==========================
        # 2.1 Preprocessing
        # ==========================
            # ==========================
            # 2.1.1 Update States
            # ==========================
            StImplement = Implements[:, 3]
            StTask = Tasks[:, 4]
            StVehicle = Vehicles[:, 5]

            num_implements = len(Implements)
            num_tasks = len(Tasks)
            num_vehicles = len(Vehicles)

            # ==========================
            # 2.1.2 Dynamic Variables
            # ==========================
            Vhat = np.ones((num_periods, num_vehicles)).astype(int)
            Ihat = np.ones((num_periods, num_implements)).astype(int)
            Khat = np.ones((num_periods, num_tasks), dtype=int).astype(int)
            Khat[1:num_periods][:] = 0

            if t==0: 
                M= Tasks[:, 3]
            else: 
                M = (200*(math.log10(t)))+Tasks[:, 3]

            That = Vehicles[:, 4]
            T_max = Vehicles[:, 3]

            I = [i for i, State in enumerate(StImplement) if State == 0]
            K = [k for k, State in enumerate(StTask) if State == 0]
            V = [i for i, State in enumerate(StVehicle) if State == 0]
            Tau = range(num_periods)

            # ==========================
            # 2.1.3 Cost and Energy Calculations
            # ==========================
            Cd, Bd = ct.DynamicCalculation(num_implements, num_tasks, num_vehicles, Implements, Tasks, Vehicles)
            Cst, Bst = ct.StaticCalculation(num_implements, num_tasks, num_vehicles, Implements, Tasks, Vehicles)
            Cprime = ct.PrimeCalculation(num_implements, num_tasks, num_vehicles, Implements, Tasks, Vehicles)

            if num_periods > 1:
                Cst, Cd, Bst, Bd, M, Cprime = ct.TimeExtendCalculation(
                    num_periods, num_implements, num_tasks, num_vehicles, Cst, Cd, Bst, Bd, M, Cprime, Tasks
                )
            b = (EnergyBalance[0] * Bst + EnergyBalance[1] * Bd).astype(int)

            # ==========================
            # 2.1.4 Compatibility Data
            # ==========================
            os.chdir(dir)
            IK, KI, IV, VI, KV, VK = dt.CompatibilityData(num_implements, num_tasks, num_vehicles, full, set_data)
            os.chdir(dir)

        # ==========================
        # 2.2 Optimization Model
        # ==========================
            Error = 10
            while Error > 5:
                # Combine static and dynamic costs
                C = (CostBalance[0] * Cst + CostBalance[1] * Cd).astype(int)
                Cmax, Mmax = ct.NormalicedCalculation(num_periods, M, I, K, V, C, Cprime)

                # Select optimization model based on the number of periods
                if num_periods <= 1:
                    modelo = sm.Optimization(C, M, That, I, K, V, Mmax, Cmax, IK, KI, IV, VI, KV, VK, alpha, beta, b, Cprime, Tmin)
                else:
                    modelo = dm.Optimization(
                        C, M, That, I, K, V, Mmax, Cmax, IK, KI, IV, VI, KV, VK, alpha, beta, T_max, b, Tau, Vhat, Ihat, Khat, Cprime, Tmin
                    )

                os.chdir(dir)

                # Handle infeasible models
                if modelo.Status == GRB.Status.INFEASIBLE:
                    print("The model is infeasible. Stopping optimization.")
                    modelo.write("infeasible_model.ilp")  # Save the model for analysis
                    break

                # Extract solution variables
                try:
                    all_vars = modelo.getVars()
                    tprime = modelo.getAttr("Runtime")
                    values = modelo.getAttr("X", all_vars)
                    names = modelo.getAttr("VarName", all_vars)
                    XAsignments = {name: val for name, val in zip(names, values) if (val > 0 and name.startswith('x'))}
                    ZAsignments = {name: val for name, val in zip(names, values) if (val > 0 and name.startswith('z'))}
                    if num_periods > 1:
                        TAsignments = {name: val for name, val in zip(names, values) if (val > 0 and name.startswith('T'))}
                except:
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

  
        if Event[0]==False: 
            Event,Vehicles,Implements,Tasks,AssignmentT,depot_info,tmo,Distancia,totalDistancia=mv.custom_animation(Implements, Tasks, Vehicles, XAsignments,ZAsignments,probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA,0,totalDistancia,num_periods)
        
        # ==========================
        # 2.4 PostProcessing
        # ==========================
        t=t+(tmo)
        if Event[0]:  
            XAsignments,InfoTaskDone,ZAsignments=pop.AssignmentDone(AssignmentT,t,InfoTaskDone,M,depot_info)
            try:
                Implements,Tasks,Vehicles,M,That=pp.UpdateInfoST(XAsignments,Implements,Tasks,Vehicles,M,That,b,ZAsignments,T_max,Distancia)
            except:
                Implements,Tasks,Vehicles,M,That=pp.UpdateInfoTE(XAsignments,Implements,Tasks,Vehicles,M,That,num_periods,ZAsignments,b,T_max,TAsignments,num_vehicles)

            # ==========================
            # 2.4.1 Update List
            # ==========================
        
        AssigmentDone.append(XAsignments)
        try:
            AssigmentDoneList=pop.AssignmentByRobot(AssigmentDone)
        except:
            pass
        t=t+(tmo)


            # ==========================
            # 2.4.2 Event Processing
            # ==========================

        if Event[0]:  
            if Event[1]=="Task":
                EventProcess = EV.TaskEvent("Task event", Event[2],1)
                NTasks = EventProcess.process()
                Tasks=np.concatenate((Tasks,NTasks),axis=0) 
                EventLogger.log_event(EventProcess)
               
            elif Event[1]== "Vehicle" :
                EventProcess = EV.VehicleEvent("New Vehicle", Event[2],Vehicles,1,data)
                Vehicles = EventProcess.process()
                EventLogger.log_event(EventProcess)
            elif Event[1]=="Implement":
                EventProcess = EV.ImplementEvent("New Implement", Event[1],1)
                NImplements =EventProcess.process()
                EventLogger.log_event(EventProcess)
            elif Event[1]=="Simulation":
                if Event[2]==2:
                    SimulationData = [ZAsignments,That,T_max]
                else:
                    SimulationData = []
                EventProcess = EV.SimulationEvent("Simulation Event", Event[2],SimulationData) 
                SimulationOutput=EventProcess.process()
                EventLogger.log_event(EventProcess)
                if Event[2]==2:
                    That=SimulationOutput[0]
                    Vehicles[:,4]=That
                    T_max=SimulationOutput[1]
            else:
                print("Error: EVENT NOT FOUND")

        Info=EventLogger.get_events_by_type()
        Info=len(Info)

        # ==========================
        # 2.5 Visualization of results
        # ==========================
        

        try:
            RobotPerformanceList=[[f"Task done by Robot {i}",AssigmentDoneList[i]["TaskCount"]] for i in AssigmentDoneList.keys()]
        except:
            try: 
                RobotPerformanceList=RobotPerformanceList
            except:
                RobotPerformanceList=[]

        That_list = [[f"Battery of vehicule {i}", int(That[i])] for i in range(num_vehicles)]
        Distancia_list = [[f"Distance of vehicule {i}", round(totalDistancia[i],2)] for i in range(num_vehicles)]
        summary_data = [
            *That_list,
            *Distancia_list,
            *RobotPerformanceList,
            ["Total distance", round(sum(totalDistancia), 2)],
            ["Elapsed time", round(t,3)],
            ["Elapsed time of optimization", round(toptimization,5)],
            ["Number of events",Info]
        ]


        with open(DATA_FILE, "w") as file:
            json.dump(summary_data, file, indent=4)


        K=[k for k, State in enumerate(StTask) if State == 0]
        if len(K)==0:
            Tasks=[]


    

    
    # ========================== CALCULETE OBJECTIVE FUNCTION ===================================
    CostDistance,DoneAsignationCost,StaticCostTask=pop.TrueObj(totalDistancia, InfoTaskDone,AssigmentDoneList, EfVehicle,aTasck,EfImplement)
    Obj = CostDistance + DoneAsignationCost+ StaticCostTask
    return t,toptimization,Obj,DoneAsignationCost,StaticCostTask,Distancia_list,RobotPerformanceList



# init(Implements,Tasks,Vehicles,T)
