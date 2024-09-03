import numpy as np
import pandas as pd
import Data as dt
from View import StView as vw
from View import TEView as tew
from View import Movement as mv
from View import TEMovement as temv
from Models import StaticModel_NOGUROBY as sm
from Models import DynamicModel as dm
from Models import StaticModel as smG
from pyscipopt import Model as Modelo
import os
import Cost as ct
import Preprocessing as pp
import PostProcessing as pop
import matplotlib.pyplot as plt
import math
from Events import EventLogger as EVlogger
from Events import Events as EV
from tabulate import tabulate



#Initial data (open fleet)
# set_data = 5
# num_implements = 10
# num_tasks = 20
# num_vehicles = 5
# num_periods = 1
# T=40

# dir=os.getcwd()
# os.chdir(dir)
# Implements,Tasks,Vehicles=dt.PositionData(num_implements,num_tasks,num_vehicles,set_data)



def init(Implements,Tasks,Vehicles,T,num_periods,probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA):
    InfoTaskDone=[]
    data=1
    t=0
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
    TotalDistancia = np.ones((len(Vehicles)),dtype=float)
    Distancia=np.ones((len(Vehicles)),dtype=float)
    T_max=Vehicles[:,3]
    CostBalance = [1,1]
    alpha,beta=0.5,0.5
    EnergyBalance = [1,1]
    Tmin=20
    num_vehicles = len(Vehicles)
    full=True #Compatibilidad : true compatibiladad todos con todos
    dir=os.getcwd()
    EventLogger=EVlogger.EventLogger()



    while((len(Tasks)>0) and (t<T)):
        if Event[0]:
            Obj_prime=0
            Event[0]= False
            #Update the number of Implements, Tasks and Vehicles
            num_implements = len(Implements)
            num_tasks = len(Tasks)
            num_vehicles = len(Vehicles)
           
            Vhat = Ihat = np.ones((num_periods,num_vehicles)).astype(int)
            Khat = np.ones((num_periods,num_tasks),dtype=int).astype(int)
            Khat[1:num_periods][:]=0

            M=Tasks[:,3]
            That=Vehicles[:,4]
            T_max=Vehicles[:,3]
            I=range(num_implements)
            K=range(num_tasks)
            V=range(num_vehicles)
            Tau=range(num_periods)

            #Calculation of the cost and energy consumition

            Cd,Bd=ct.DynamicCalculation(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles)
            Cst,Bst=ct.StaticCalculation(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles)
            Cprime=ct.PrimeCalculation(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles)
            if num_periods>1:
                Cst,Cd,Bst,Bd,M,Cprime=ct.TimeExtendCalculation(num_periods,num_implements,num_tasks,num_vehicles,Cst,Cd,Bst,Bd,M,Cprime,Tasks)
            C=(CostBalance[0]*Cst+CostBalance[1]*Cd).astype(int)
            b=(EnergyBalance[0]*Bst+EnergyBalance[1]*Bd).astype(int)
            Cmax,Mmax=ct.NormalicedCalculation(num_periods,M,range(num_tasks))


            #Compatibility data
            os.chdir(dir)
            IK,KI,IV,VI,KV,VK=dt.CompatibilityData(num_implements,num_tasks,num_vehicles,full)

            #Optimization model
            if num_periods<=1:
                modelo=smG.Optimization(C,M,That,I,K,V,Mmax,Cmax,IK,KI,IV,VI,KV,VK,alpha,beta,b,Cprime,Tmin)
            else:
                modelo=dm.Optimization(C,M,That,I,K,V,Mmax,Cmax,IK,KI,IV,VI,KV,VK,alpha,beta,T_max,b,Tau,Vhat,Ihat,Khat,Cprime,Tmin)
            
            os.chdir(dir)
            #modelo.write("model"+str(i)+".lp")
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
                    



            #Visualization
            # if num_periods<=1:
            #     vw.init(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles,XAsignments,M,That,ZAsignments)
            # else:
            #     tew.init(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles,XAsignments,M,num_periods,ZAsignments,TAsignments)
            os.chdir(dir)
            t=t+tprime
        

        if num_periods<=1:
            Event,Vehicles,Implements,Tasks,AssignmentT,tmo,Distancia=mv.animate_allocation(Implements, Tasks, Vehicles, XAsignments,ZAsignments,probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA)
        else:
            Event,Implements,Tasks,Vehicles=temv.animate_allocation(Implements, Tasks, Vehicles, XAsignments,ZAsignments,probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA)
        

        #Postprocessing:
        t=t+(tmo)
        if Event[0]:  
            XAsignments,InfoTaskDone=pop.AssignmentDone(AssignmentT,t,InfoTaskDone,M)
            if num_periods<=1:
                Implements,Tasks,Vehicles,M,That=pp.UpdateInfoST(XAsignments,Implements,Tasks,Vehicles,M,That,b,ZAsignments,T_max,Distancia)
            else:
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
                    T_max=SimulationOutput[1]
            else:
                print("Error: EVENT NOT FOUND")

        Info=EventLogger.get_events_by_type()
        Info=len(Info)
        Obj_prime=CostPenaltyRest+CostDistance_prime+DoneAsignationCost
        Obj+=Obj_prime

        That_list = [[f"Battery of vehicule {i+1}", int(That[i])] for i in range(num_vehicles)]
        Distancia_list = [[f"Distance of vehicule {i+1}", int(Distancia[i])] for i in range(num_vehicles)]
        summary_data = [
            *That_list,
            *Distancia_list,
            ["Elapsed time", t],
            ["Cost of penalty of task do not finish", CostPenaltyRest],
            ["Cost of task done", DoneAsignationCost],
            ["Cost of distance", CostDistance_prime],
            ["Total objective value (this iteration)", Obj_prime],
            ["Total objective value", Obj],
            ["Number of events",Info]
        ]

        print(tabulate(summary_data, headers=["Description", "Value"], tablefmt="rst"))

    

    

    print("El valor objetivo final es de:",Obj)



# init(Implements,Tasks,Vehicles,T)
