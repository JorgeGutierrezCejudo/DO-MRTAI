"""
TimeExtendSMC.py - Time-Extended Multi-Robot Task Assignment Optimization Model

This module implements the time-extended (multi-period) optimization model for the D-MRTAI problem.
It extends the static model to consider multiple time periods, allowing vehicles to perform multiple
tasks sequentially while managing battery consumption and recharging.

Key Features:
- Multi-period assignment optimization with time-indexed variables
- Dynamic battery management with recharging at depot
- Task availability tracking across periods
- Continuous battery level variables for accurate energy management
- Vehicle, implement, and task availability matrices across periods

Decision Variables:
- x[i,k,v,t]: Binary, 1 if implement i with vehicle v performs task k in period t
- y[k,t]: Binary, 1 if task k is assigned in period t
- z[v,t]: Binary, 1 if vehicle v returns to depot in period t
- o[k,t]: Binary, 1 if task k is still available (not yet completed) in period t
- T[v,t]: Continuous, battery level of vehicle v at the start of period t

Objective:
Minimize: alpha * (sum of normalized costs over all periods) + beta * (penalties for unassigned tasks)

Key Constraints:
- Task completion tracking: once completed, task is no longer available
- Battery dynamics: discharge during tasks, recharge at depot
- Entity availability per period (from Vhat, Ihat, Khat matrices)
- Battery bounds: Tmin <= T[v,t] <= T_max[v]

Author: Jorge
Date: 2024
"""

import copy as copy
from gurobipy import *
from gurobipy import GRB
import numpy as np
import pandas as pd
import os


def Optimization (C,M,That,I,K,V,Mmax,Cmax,IK,KI,IV,VI,KV,VK,alpha,beta,T_max,b,Tau,Vhat,Ihat,Khat,Cprime,Tmin):
    """
    Create and solve the time-extended assignment optimization model.
    
    This model extends the static case to multiple time periods, allowing vehicles to:
    - Perform multiple tasks across periods
    - Return to depot to recharge battery
    - Track task completion status across time
    
    Args:
        C (np.array): Cost matrix [num_periods x num_implements x num_tasks x num_vehicles]
        M (np.array): Penalty matrix [num_periods x num_tasks]
        That (np.array): Initial battery level for each vehicle [num_vehicles]
        I (list): List of available implement indices
        K (list): List of available task indices
        V (list): List of available vehicle indices
        Mmax (float): Normalization constant for penalties
        Cmax (list): Normalization constants for costs per vehicle [num_vehicles]
        IK, KI, IV, VI, KV, VK (np.array): Compatibility matrices
        alpha (float): Weight for cost component in objective
        beta (float): Weight for penalty component in objective
        T_max (np.array): Maximum battery capacity for each vehicle [num_vehicles]
        b (np.array): Energy consumption [num_periods x num_implements x num_tasks x num_vehicles]
        Tau (range): Time period indices (e.g., range(3) for 3 periods)
        Vhat (np.array): Vehicle availability [num_periods x num_vehicles]
        Ihat (np.array): Implement availability [num_periods x num_implements]
        Khat (np.array): Task availability [num_periods x num_tasks]
        Cprime (np.array): Depot return cost [num_periods x num_vehicles]
        Tmin (float): Minimum battery threshold
        
    Returns:
        model: Gurobi model object with the solution (if feasible)
    """
    # ===================================
    # Recalculate Cost Normalization
    # ===================================
    # For each vehicle, sum the maximum cost across all periods
    Cmax = [0] * len(V)
    for v in V:
        Cmax[v] = sum(
            Vhat[t, v] * max(Cprime[t, v], np.max(C[t, :, :, v])) for t in Tau
        )

    # ===================================
    # Model Initialization
    # ===================================
    model = Model('TimeExtendedMRTAI-MultiPeriod')
    
    # Set solver parameters
    timeLimit = 1000  # Maximum solving time in seconds
    model.setParam('TimeLimit', timeLimit)

    # ===================================
    # Decision Variables
    # ===================================
    # x[i,k,v,t]: Binary, 1 if implement i with vehicle v performs task k in period t
    # Only create variables for compatible combinations
    x = {(i,k,v,t):model.addVar(vtype=GRB.BINARY, name="x_" + str(i) + "_" + str(k) + "_" + str(v)+ "_" + str(t)) 
                    for i in I for k in K for v in V for t in Tau if IK[i, k] == 1 and IV[i, v] == 1 and VK[v, k] == 1}

    # y[k,t]: Binary, 1 if task k is assigned (performed) in period t
    y = {(k,t): model.addVar(vtype=GRB.BINARY, name="y_" + str(k)+ "_" + str(t))
                    for k in K for t in Tau
            }
    
    # z[v,t]: Binary, 1 if vehicle v returns to depot in period t
    z = {(v,t): model.addVar(vtype=GRB.BINARY, name="z_" + str(v)+ "_" + str(t))
                    for v in V for t in Tau
            }
    
    # o[k,t]: Binary, 1 if task k is still outstanding (not yet completed) in period t
    o = {(k,t):model.addVar(vtype=GRB.BINARY, name="O_" + str(k) + "_" + str(t)) for k in K for t in Tau}

    # T[v,t]: Continuous, battery level of vehicle v at the start of period t
    T = {(v,t):model.addVar(vtype=GRB.CONTINUOUS, name="T_" + str(v) + "_" + str(t)) for v in V for t in Tau}


    # ===================================
    # Objective Function
    # ===================================
    # Minimize: alpha * (total normalized costs across periods) + beta * (penalties for incomplete tasks)
    # The penalty term (o[k,t] - y[k,t]) represents tasks that are available but not assigned
    obj = (alpha) * quicksum(
        quicksum(
            quicksum(
                C[t][i][k][v] * x[i, k, v, t]
                for i in I for k in K if (i, k, v, t) in x
            ) + Cprime[t][v] * z[v, t]  # Add depot return cost
            for t in Tau
        ) / (Cmax[v])  # Normalize by vehicle
        for v in V
    ) + (beta / (Mmax)) * quicksum(
        M[t][k] * (o[k, t] - y[k, t]) for k in K for t in Tau  # Penalty for outstanding tasks
    )

    model.setObjective(obj, GRB.MINIMIZE) 

    # ===================================
    # Constraints
    # ===================================
    
    # Constraint 31: Implement assignment constraint
    # Each implement can be assigned to at most one task in each period (respecting availability)
    for i in I:
        for t in Tau:
            model.addConstr(quicksum(x[i, k, v,t] for k in K for v in V if IK[i,k]==1 and IV[i,v]==1 and KV[k,v]==1) <= Ihat[t][i],
                           name=f"implement_{i}_period_{t}_assignment")
    
    # Constraint 33: Task assignment consistency
    # If task k is assigned in period t, exactly one implement-vehicle pair performs it
    for k in K:
        for t in Tau:
            model.addConstr(quicksum(x[i, k, v,t] for i in I for v in V if IK[i,k]==1 and IV[i,v]==1 and KV[k,v]==1) == y[k,t],
                           name=f"task_{k}_period_{t}_assignment")

    # Constraint 32: Vehicle assignment exclusivity per period
    # Each vehicle either performs one task or returns to depot in each period (respecting availability)
    for v in V:
        for t in Tau:
            model.addConstr(z[v,t] + quicksum(x[i, k, v, t] for i in I for k in K if IK[i,k]==1 and IV[i,v]==1 and KV[k,v]==1) == Vhat[t][v],
                           name=f"vehicle_{v}_period_{t}_single_action")

    # Battery capacity constraint per period
    # Energy consumption in period t must not deplete battery below minimum threshold
    for v in V:
        for t in Tau:
            model.addConstr(quicksum((b[t][i][k][v]) * x[i, k, v,t] for i in I for k in K) <= T[v,t]-Tmin,
                           name=f"vehicle_{v}_period_{t}_battery")
    
    # Constraint: Task can only be assigned if it's still outstanding
    for k in K:
        for t in Tau:
            model.addConstr(y[k,t] <= o[k,t],
                           name=f"task_{k}_period_{t}_outstanding")
    
    # ===================================
    # Task Availability Dynamics
    # ===================================
    
    # Constraint 34: Initial task availability
    # At t=0, task availability is determined by Khat matrix
    for k in K:
        model.addConstr(o[k,0] == Khat[0][k],
                       name=f"task_{k}_initial_availability")
    
    # Constraint 35: Task availability propagation
    # Task remains available until completed, may have new tasks appear (Khat)
    # o[k,t+1] = o[k,t] - y[k,t] + Khat[t+1,k]
    for k in K:
        for t in range(len(Tau) - 1):
            model.addConstr(o[k, t + 1] == o[k, t] - y[k,t] + Khat[t+1][k],
                           name=f"task_{k}_period_{t}_availability_propagation")

    # ===================================
    # Battery Dynamics Constraints
    # ===================================
    
    # Constraint 36: Initial battery level
    # At t=0, battery level is the input That
    for v in V:
        model.addConstr(T[v,0] == That[v],
                       name=f"vehicle_{v}_initial_battery")

    # Constraint 37: Battery discharge lower bound
    # Battery at t+1 >= Battery at t - energy consumed
    for v in V:
        for t in range(len(Tau) - 1):
            model.addConstr(T[v,t + 1] >= T[v,t] - quicksum((b[t][i][k][v]) * x[i, k, v, t] for i in I for k in K if IK[i,k]==1 and IV[i,v]==1 and KV[k,v]==1),
                           name=f"vehicle_{v}_period_{t}_battery_discharge_lb")

    # Constraint 38: Battery dynamics upper bound with recharging
    # Battery at t+1 <= Battery at t - energy consumed + full recharge if at depot
    # If z[v,t]=1 (at depot), battery can be recharged to T_max
    for v in V:
        for t in range(len(Tau) - 1):
            model.addConstr(T[v,t + 1] <= T[v,t] - quicksum((b[t][i][k][v]) * x[i, k, v, t] for i in I for k in K if IK[i,k]==1 and IV[i,v]==1 and KV[k,v]==1) + T_max[v] * z[v,t],
                           name=f"vehicle_{v}_period_{t}_battery_recharge_ub")

    # Constraint 39: Recharge guarantee
    # If vehicle goes to depot (z[v,t]=1), battery at t+1 must be at least T_max (full recharge)
    for v in V:
        for t in range(len(Tau) - 1):
            model.addConstr(T[v,t + 1] >= T_max[v] * z[v, t],
                           name=f"vehicle_{v}_period_{t}_recharge_guarantee")

    # Constraint 40: Battery bounds
    # Battery level must stay within [Tmin, T_max] at all times
    for v in V:
        for t in Tau:
            model.addConstr(T[v,t] >= Tmin,
                           name=f"vehicle_{v}_period_{t}_battery_min")
            model.addConstr(T[v,t] <= T_max[v],
                           name=f"vehicle_{v}_period_{t}_battery_max")

    # ===================================
    # Solve the Model
    # ===================================
    model.optimize()

    return model


########################################################### DYNAMIC INSTANCE ############################################################################################################

# def CalculateCompMatrices (IK,IV):
#     # Calculate VK (compatibility between vehicle and task)
#     VK = (np.dot(IV.T, IK) > 0).astype(int)

#     # Calculate KV (transpose of VK)
#     KV = VK.T

#     # Calculate KI (transpose of IK)
#     KI = IK.T

#     # Calculate VI (transpose of IV)
#     VI = IV.T

#     return VK,KV,VI,KI
    
# CostBalance = [1,0.01]
# EnergyBalance = [1,0.2]
# GlobalResults={}
# num_periods=2
# num_implements=3
# num_tasks=6
# num_vehicles=3
# set_data=1
# full=True
# directory_path="Parameters-("+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+","+str(num_periods)+")-"+str(set_data)
# print("Running optimization for", num_implements, "implements,", num_tasks, "tasks and", num_vehicles, "vehicles.")


# try:
#     os.chdir(directory_path)
#     Cst = np.loadtxt('Cst.csv', delimiter=',', dtype=int).reshape(num_periods,num_implements, num_tasks, num_vehicles)
#     Cd = np.loadtxt('Cd.csv', delimiter=',', dtype=int).reshape(num_periods,num_implements, num_tasks, num_vehicles)
#     M = np.loadtxt('M.csv', delimiter=',', dtype=int).reshape(num_periods,num_tasks)
#     T_max = np.loadtxt('T_max.csv', delimiter=',', dtype=int)
#     That = np.loadtxt('T.csv', delimiter=',', dtype=int)
#     That = np.array(That)
#     bst = np.loadtxt('bst.csv', delimiter=',', dtype=int).reshape(num_periods,num_implements, num_tasks, num_vehicles)
#     bd = np.loadtxt('bd.csv', delimiter=',', dtype=int).reshape(num_periods,num_implements, num_tasks, num_vehicles)
#     C=(CostBalance[0]*Cst+CostBalance[1]*Cd).astype(int)
#     b=(EnergyBalance[0]*bst+EnergyBalance[1]*bd).astype(int)
#     Cprime = np.loadtxt('Cprime.csv', delimiter=',', dtype=int).reshape(num_periods,num_vehicles)
#     print("............................................................")
#     print("Data exists, loading data from files")
#     print("............................................................")

# except:
#     print("............................................................")
#     print("Data does not exist, creating data and saving to files")
#     print("............................................................")
#     os.makedirs(directory_path)
#     os.chdir(directory_path)
#     np.random.seed(set_data)  
#     Cst = np.random.randint(1, 100, size=(num_implements, num_tasks, num_vehicles))
#     np.random.seed(set_data+10)  
#     Cd = np.random.randint(1, 100, size=(num_implements, num_tasks, num_vehicles))
#     np.random.seed(set_data)  
#     M = np.random.randint(1, 2000, size=(num_tasks))
#     np.random.seed(set_data)  
#     T_max = np.random.randint(100,200, size=(num_vehicles)) 
#     np.random.seed(set_data)  
#     That = [np.random.randint(0.8*T_max[i], T_max[i]) for i in range(num_vehicles)]
#     np.random.seed(set_data)  
#     That = np.array(That)

#     if num_periods>1:
#         Cst_pivot=Cst
#         Cd_pivot=Cd
#         M_pivot=M

#         for _ in range(num_periods-1):
#             Cstt = np.random.normal(loc=Cst, scale=1).astype(int)
#             Cst_pivot = np.concatenate((Cst_pivot, Cstt))
#             Cdt = np.random.uniform(np.max(Cd),np.max(Cd)+1,size=(num_implements,num_tasks,num_vehicles)).astype(int)
#             Cd_pivot = np.concatenate((Cd_pivot, Cdt))
#             Mt = np.random.normal(loc=M, scale=1).astype(int)
#             M_pivot = np.concatenate((M_pivot, Mt))

#     Cst=Cst_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)
#     Cd=Cd_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)
#     M=M_pivot.reshape(num_periods,num_tasks)

#     np.random.seed(set_data) 
#     bst = np.random.randint(1, 20, size=(num_implements, num_tasks, num_vehicles))
#     np.random.seed(set_data+10)
#     bd = np.random.randint(1, 20, size=(num_implements, num_tasks, num_vehicles))
#     if num_periods>1:
#         bst_pivot=bst
#         bd_pivot=bd

#         for _ in range(num_periods-1):
#             bstt = np.random.normal(loc=bst, scale=1).astype(int)
#             bst_pivot = np.concatenate((bst_pivot, bstt))
#             bdt = np.random.uniform(np.max(bd),np.max(bd)+1,size=(num_implements,num_tasks,num_vehicles)).astype(int)
#             bd_pivot = np.concatenate((bd_pivot, bdt))

#     bst=bst_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)
#     bd=bd_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)
#     np.random.seed(set_data)
#     Cprime = np.random.randint(1, 100, size=(num_periods,num_vehicles))       
                        
#     b=(EnergyBalance[0]*bst+EnergyBalance[1]*bd).astype(int)
#     C=(CostBalance[0]*Cst+CostBalance[1]*Cd).astype(int)

#     # Guardar en archivos CSV
#     bst_reshaped = bst.reshape(-1, num_vehicles)
#     bd_reshaped = bd.reshape(-1, num_vehicles)
#     Cprime_reshaped = Cprime.reshape(-1, num_vehicles)
#     Cst_reshaped = Cst.reshape(-1, num_vehicles)
#     Cd_reshaped = Cd.reshape(-1, num_vehicles)
#     M_reshaped = M.reshape(num_periods, -1)
#     T_max_reshaped = T_max.reshape(1, -1)
#     That_reshaped = np.array(That).reshape(1, -1)

#     # Guardar en archivos CSV
#     pd.DataFrame(Cprime_reshaped).to_csv('Cprime.csv', index=False, header=False)
#     pd.DataFrame(bst_reshaped).to_csv('bst.csv', index=False, header=False)
#     pd.DataFrame(bd_reshaped).to_csv('bd.csv', index=False, header=False)
#     pd.DataFrame(Cst_reshaped).to_csv('Cst.csv', index=False, header=False)
#     pd.DataFrame(Cd_reshaped).to_csv('Cd.csv', index=False, header=False)
#     pd.DataFrame(M_reshaped).to_csv('M.csv', index=False, header=False)
#     pd.DataFrame(T_max_reshaped).to_csv('T_max.csv', index=False, header=False)
#     pd.DataFrame(That_reshaped).to_csv('T.csv', index=False, header=False)


# I=range(num_implements)
# V=range(num_vehicles)
# K=range(num_tasks)


# if num_periods==1:
#     Cmax=1
#     Mmax=sum(M[0][k] for k in K for t in range(num_periods))
# else:
#     Cmax=1
#     Mmax=sum(M[0][k] for k in K for t in range(num_periods))

# directory_path="Compatibility-("+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+")"
# if full==True:        
#     IV = np.ones((num_implements, num_vehicles)) 
#     IK = np.ones((num_implements, num_tasks)) 
#     VK,KV,VI,KI=CalculateCompMatrices(IK,IV)

# else:
#     if os.path.exists(directory_path):

#         os.chdir(directory_path)
#         IK=np.loadtxt('IK.csv', delimiter=',', dtype=int)
#         IV =np.loadtxt('IV.csv', delimiter=',', dtype=int)        
#         VK,KV,VI,KI=CalculateCompMatrices(IK,IV)

#     else:
#         np.random.seed(set_data)
#         IK = np.random.randint(0, 2, size=(num_implements, num_tasks))  # Implements x Tasks
#         IV = np.random.randint(1, 2, size=(num_implements, num_vehicles))  # Implements x Vehicles
#         os.makedirs(directory_path)
#         os.chdir(directory_path)
#         VK,KV,VI,KI=CalculateCompMatrices(IK,IV)
#         pd.DataFrame(IK).to_csv('IK.csv', index=False, header=False)
#         pd.DataFrame(IV).to_csv('IV.csv', index=False, header=False)
#         pd.DataFrame(VK).to_csv('VK.csv', index=False, header=False)
# alpha,beta,=0.5,0.5
# gamma=0


# Tau = range(num_periods)
# Vhat = Ihat = np.ones((num_periods,num_vehicles))
# Ihat = np.ones((num_periods,num_implements))
# Khat = np.ones((num_periods,num_tasks),dtype=int)
# Khat[1:num_periods][:]=0
# Tmin=15
# list={}
# list["T_max"]=T_max
# list["b"]=b
# list["Tau"]=Tau
# list["Vhat"]=Vhat
# list["Ihat"]=Ihat
# list["Khat"]=Khat
# list["Cprime"]=Cprime
# list["Tmin"]=Tmin


# # print(list)
# # # # # ###################################################################### RUN MODELS ############################################################################################################

# modelo=Optimization (C,M,That,I,K,V,Mmax,Cmax,IK,KI,IV,VI,KV,VK,alpha,beta,**list)
# # model.write("model.lp")
# # all_vars = model.getVars()
# # values = model.getAttr("X", all_vars)
# # names = model.getAttr("VarName", all_vars)  


# # tot_var = {name: val for name,val in zip(names, values) if val>0}
# # variables_count = {'x': 0, 'y': 0, 'z': 0}
# # for key in tot_var:
# #     if key.startswith('x'):
# #         variables_count['x'] += 1
# #     elif key.startswith('y'):
# #         variables_count['y'] += 1
# #     elif key.startswith('z'):
# #         variables_count['z'] += 1
    
# # print(variables_count)
# modelo.write("modelo.lp")
# all_vars = modelo.getVars()
# values = modelo.getAttr("X", all_vars)
# names = modelo.getAttr("VarName", all_vars)
# tot_var = {name: val for name,val in zip(names, values) if val>0}
# print(tot_var)
# num_z_values = 0
# num_z_values = sum(1 for asignacion in tot_var.keys() if asignacion.startswith('z'))
# # GlobalResults[str(i)]={"Runtime":modelo.Runtime,"ObjVal":modelo.ObjVal,"MIPGap":modelo.MIPGap,"Robot in the depot":num_z_values}
# # new_dir = os.path.abspath(os.path.join(os.getcwd(), "../../../"))

# # # Cambiar el directorio de trabajo
# # os.chdir(new_dir)

# # # Cambiar el directorio de trabajo


# # df = pd.DataFrame({'Result':GlobalResults.values()})
# # df.to_csv("ResultDynamic-"+str(j)+str(k)+"CostBalance"+str(m)+".csv", mode='a', header=True, index= False)



#     # # # model.write("model.lp")
#     # # all_vars = model.getVars()
#     # # values = model.getAttr("X", all_vars)
#     # # names = model.getAttr("VarName", all_vars)
#     # # tot_var = {name: val for name,val in zip(names, values) if val>0}
#     # # variables_count = {'x': 0, 'y': 0, 'z': 0}
#     # # for key in tot_var:
#     # #     if key.startswith('x'):
#     # #         variables_count['x'] += 1
#     # #     elif key.startswith('y'):
#     # #         variables_count['y'] += 1
#     # #     elif key.startswith('z'):
#     # #         variables_count['z'] += 1

#     # # print(variables_count)
#     # # print("..............................................................................")
#     # # print(tot_var)