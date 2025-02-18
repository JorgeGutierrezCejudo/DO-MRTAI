import numpy as np
import json
import pandas as pd
import Data as dt
from View import StView as vw
from View import TEView as tew
from View import Movement as mv
from Models import StaticModelSMC as sm
from Models import DynamicModelSMC as dm
import os
import Cost as ct
import Preprocessing as pp
import PostProcessing as pop
import matplotlib.pyplot as plt
import math
from Events import EventLogger as EVlogger
from Events import Events as EV
from tabulate import tabulate
from ROS import RealCost as rc
import time
import roslibpy
from gurobipy import GRB



#Initial data (open fleet)
# set_data = 5
# num_implements = 10
# num_tasks = 20
# num_vehicles = 5
# num_periods = 1
# T=40
# Implements,Tasks,Vehicles=dt.PositionData(num_implements,num_tasks,num_vehicles,set_data)



def init(Implements,Tasks,Vehicles,T,num_periods,probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA,full,set_data):
    DATA_FILE = "simulation_data.json"
    InfoTaskDone=[]
    data=1
    t=0
    toptimization=0
    Obj=0
    CostPenaltyRest=0
    DoneAsignationCost=0
    CostDistance= 0
    Event=[True,"",0]
    XAsignments={}
    ZAsignments={}
    TAsignments={}
    M=Tasks[:,3]
    That=Vehicles[:,4]
    b=0
    totalDistancia = np.ones((len(Vehicles)),dtype=float)
    Distancia=np.ones((len(Vehicles)),dtype=float)
    T_max=Vehicles[:,3]
    CostBalance = [0,1]
    alpha,beta=0.05,0.95
    EnergyBalance = [1,1]
    Tmin=0
    num_vehicles = len(Vehicles)
    dir=os.getcwd()
    EventLogger=EVlogger.EventLogger()
    # client = roslibpy.Ros(host="192.168.1.54", port=9090)
    # client.run()
    # print("Connected with ROS")



    while((len(Tasks)>0) and (t<T)):
        if Event[0]:
            Obj_prime=0
            Event[0]= False
            #Update the number of Implements, Tasks and Vehicles
            StImplement=Implements[:,3]
            StTask=Tasks[:,4]
            StVehicle=Vehicles[:,5]
            num_implements = len(Implements)
            num_tasks = len(Tasks)
            num_vehicles = len(Vehicles)



            Vhat =  np.ones((num_periods,num_vehicles)).astype(int)
            Ihat =  np.ones((num_periods,num_implements)).astype(int)
            Khat = np.ones((num_periods,num_tasks),dtype=int).astype(int)
            Khat[1:num_periods][:]=0
            num_implements = len(Implements)
            num_tasks = len(Tasks)
            num_vehicles = len(Vehicles)

            M=Tasks[:,3]
            That=Vehicles[:,4]
            T_max=Vehicles[:,3]

            I= [i for i, State in enumerate(StImplement) if State == 0]
            K=[k for k, State in enumerate(StTask) if State == 0]
            V=[i for i, State in enumerate(StVehicle) if State == 0]
            Tau=range(num_periods)


            #Calculation of the cost and energy consumition

            Cd,Bd=ct.DynamicCalculation(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles)
            Cst,Bst=ct.StaticCalculation(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles)
            Cprime=ct.PrimeCalculation(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles)
            if num_periods>1:
                Cst,Cd,Bst,Bd,M,Cprime=ct.TimeExtendCalculation(num_periods,num_implements,num_tasks,num_vehicles,Cst,Cd,Bst,Bd,M,Cprime,Tasks)
            b=(EnergyBalance[0]*Bst+EnergyBalance[1]*Bd).astype(int)
            


            #Compatibility data
            os.chdir(dir)
            IK,KI,IV,VI,KV,VK=dt.CompatibilityData(num_implements,num_tasks,num_vehicles,full,set_data)
            os.chdir(dir)
            #Optimization model
            Error=10
            while Error>5:
                C=(CostBalance[0]*Cst+CostBalance[1]*Cd).astype(int)
                Cmax,Mmax=ct.NormalicedCalculation(num_periods, M,I,K,V,C, Cprime)

                if num_periods<=1:
                    modelo=sm.Optimization(C,M,That,I,K,V,Mmax,Cmax,IK,KI,IV,VI,KV,VK,alpha,beta,b,Cprime,Tmin)
                else:
                    modelo=dm.Optimization(C,M,That,I,K,V,Mmax,Cmax,IK,KI,IV,VI,KV,VK,alpha,beta,T_max,b,Tau,Vhat,Ihat,Khat,Cprime,Tmin)

                os.chdir(dir)
                #modelo.write("model"+str(i)+".lp")
                if modelo.Status == GRB.Status.INFEASIBLE:
                    print("The model is infeasible. Stopping optimization.")
                    modelo.write("infeasible_model.ilp")  # Save the model for analysis
                    break
                try: 
                    all_vars = modelo.getVars()
                    tprime=modelo.getAttr("Runtime")
                    values = modelo.getAttr("X", all_vars)
                    names = modelo.getAttr("VarName", all_vars)
                    XAsignments = {name: val for name,val in zip(names, values) if ((val>0) and ((name.startswith('x'))))}
                    ZAsignments = {name: val for name,val in zip(names, values) if ((val>0) and ((name.startswith('z'))))}
                    if num_periods>1:
                        TAsignments= {name: val for name,val in zip(names, values) if ((val>0) and ((name.startswith('T'))))}
                except: 
                    XAsignments={}
                    ZAsignments={}
                    tprime=modelo.getSolvingTime()
                    solution = modelo.getBestSol()
                    all_vars = modelo.getVars()
                    # Recorrer todas las variables y filtrar por las que tienen valores mayores a 0 y empiezan con 'x' o 'z'
                    for var in all_vars:
                        val = modelo.getSolVal(solution, var)
                        name = var.name
                        if val > 0:
                            if name.startswith('x'):
                                XAsignments[name] = val
                            elif name.startswith('z'):
                                ZAsignments[name] = val
                Error=0
                # Error,Cd=rc.RealCost(XAsignments,Implements,Tasks,Vehicles,Cd,client)
                    

            #Visualization
            # if num_periods<=1:
            #     vw.init(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles,XAsignments,M,That,ZAsignments)
            # else:
            #     tew.init(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles,XAsignments,M,num_periods,ZAsignments,TAsignments)
            os.chdir(dir)
            toptimization=toptimization+tprime

  
        if Event[0]==False: 
            Event,Vehicles,Implements,Tasks,AssignmentT,depot_info,tmo,Distancia,totalDistancia=mv.custom_animation(Implements, Tasks, Vehicles, XAsignments,ZAsignments,probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA,0,totalDistancia,num_periods)
        #Postprocessing:
        t=t+(tmo)
        if Event[0]:  
            XAsignments,InfoTaskDone,ZAsignments=pop.AssignmentDone(AssignmentT,t,InfoTaskDone,M,depot_info)
            try:
                Implements,Tasks,Vehicles,M,That=pp.UpdateInfoST(XAsignments,Implements,Tasks,Vehicles,M,That,b,ZAsignments,T_max,Distancia)
            except:
                Implements,Tasks,Vehicles,M,That=pp.UpdateInfoTE(XAsignments,Implements,Tasks,Vehicles,M,That,num_periods,ZAsignments,b,T_max,TAsignments,num_vehicles)
            
        Obj=Obj-CostPenaltyRest-DoneAsignationCost

        CostPenaltyRest,DoneAsignationCost,CostDistance_prime=pop.TrueObj(Distancia,Tasks,t,M,InfoTaskDone)

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
        Obj_prime=CostPenaltyRest+CostDistance_prime+DoneAsignationCost
        Obj+=Obj_prime

        That_list = [[f"Battery of vehicule {i}", int(That[i])] for i in range(num_vehicles)]
        Distancia_list = [[f"Distance of vehicule {i+1}", int(totalDistancia[i])] for i in range(num_vehicles)]
        summary_data = [
            *That_list,
            *Distancia_list,
            ["Elapsed time", round(t,3)],
            ["Elapsed time of optimization", round(toptimization,5)],
            ["Cost of penalty of task do not finish", round(CostPenaltyRest,3)],
            ["Cost of task done", round(DoneAsignationCost,3)],
            ["Cost of distance", round(CostDistance_prime,3)],
            ["Total objective value (this iteration)", round(Obj_prime,3)],
            ["Total objective value", round(Obj,3)],
            ["Number of events",Info]
        ]


        with open(DATA_FILE, "w") as file:
            json.dump(summary_data, file, indent=4)


        K=[k for k, State in enumerate(StTask) if State == 0]
        if len(K)==0:
            Tasks=[]


    

    

    print("El valor objetivo final es de:",Obj)
    return t,toptimization,Obj,Distancia_list,InfoTaskDone



# init(Implements,Tasks,Vehicles,T)
