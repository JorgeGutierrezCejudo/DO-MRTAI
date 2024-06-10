import numpy as np
import pandas as pd
import Data as dt
from View import StView as vw
from View import TEView as tew
from View import Movement as mv
from View import TEMovement as temv
from Models import StaticModel as sm
from Models import DynamicModel as dm
import os
import Cost as ct
import Preprocessing as pp
import PostProcessing as pop
import matplotlib.pyplot as plt
import math






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



def init(Implements,Tasks,Vehicles,T,num_periods):
    t=0
    Obj=0
    Event=True
    XAsignments={}
    ZAsignments={}
    TAsignments={}
    M=Tasks[:,3]
    That=Vehicles[:,4]
    b=0
    T_max=Vehicles[:,3]
    CostBalance = [1,1]
    alpha,beta=0.5,0.5
    EnergyBalance = [1,1]
    Tmin=0
    num_vehicles = len(Vehicles)
    full=True
    dir=os.getcwd()



    while((len(Tasks)>0) and (t<T)):
        if Event==True :
            Event=False
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
                modelo=sm.Optimization(C,M,That,I,K,V,Mmax,Cmax,IK,KI,IV,VI,KV,VK,alpha,beta,b,Cprime,Tmin)
            else:
                modelo=dm.Optimization(C,M,That,I,K,V,Mmax,Cmax,IK,KI,IV,VI,KV,VK,alpha,beta,T_max,b,Tau,Vhat,Ihat,Khat,Cprime,Tmin)
            
            os.chdir(dir)
            #modelo.write("model"+str(i)+".lp")
            all_vars = modelo.getVars()
            tprime=modelo.getAttr("Runtime")
            values = modelo.getAttr("X", all_vars)
            names = modelo.getAttr("VarName", all_vars)
            XAsignments = {name: val for name,val in zip(names, values) if ((val>0) and ((name.startswith('x'))))}
            ZAsignments = {name: val for name,val in zip(names, values) if ((val>0) and ((name.startswith('z'))))}
            if num_periods>1:
                TAsignments= {name: val for name,val in zip(names, values) if ((val>0) and ((name.startswith('T'))))}


            #Visualization
            # if num_periods<=1:
            #     vw.init(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles,XAsignments,M,That,ZAsignments)
            # else:
            #     tew.init(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles,XAsignments,M,num_periods,ZAsignments,TAsignments)
            os.chdir(dir)
            t=t+tprime
        

        if num_periods<=1:
            Event,Vehicles,Implements,Tasks,AssignmentT,tmo=mv.animate_allocation(Implements, Tasks, Vehicles, XAsignments,ZAsignments)
        else:
            Event,Implements,Tasks,Vehicles=temv.animate_allocation(Implements, Tasks, Vehicles, XAsignments,ZAsignments)

        #Postprocessing:
        t=t+(tmo)
        if Event==True:     
            XAsignments=pop.AssignmentDone(AssignmentT)
            if num_periods<=1:
                Implements,Tasks,Vehicles,M,That=pp.UpdateInfoST(XAsignments,Implements,Tasks,Vehicles,M,That,b,ZAsignments,T_max)
            else:
                Implements,Tasks,Vehicles,M,That=pp.UpdateInfoTE(XAsignments,Implements,Tasks,Vehicles,M,That,num_periods,ZAsignments,b,T_max,TAsignments,num_vehicles)
        print("****************************************************")
        print(t)
        print("****************************************************")



        
    print("El valor objetivo final es de:",Obj)



# init(Implements,Tasks,Vehicles,T)
