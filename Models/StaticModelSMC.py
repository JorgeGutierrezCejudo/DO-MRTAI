"""
StaticModelSMC.py - Static Multi-Robot Task Assignment Optimization Model

This module implements the static (single-period) optimization model for the D-MRTAI problem.
It formulates and solves a Mixed Integer Programming (MIP) problem to optimally assign
tasks to robot-implement pairs while minimizing costs and penalties.

Key Features:
- Single-period assignment optimization
- Binary decision variables for task-implement-vehicle assignments
- Minimizes weighted sum of assignment costs and task penalties
- Enforces compatibility, battery, and assignment constraints
- Uses Gurobi optimizer with configurable time limits

Decision Variables:
- x[i,k,v]: Binary, 1 if implement i with vehicle v is assigned to task k
- y[k]: Binary, 1 if task k is assigned
- z[v]: Binary, 1 if vehicle v returns to depot

Objective:
Minimize: alpha * (normalized costs) + beta * (penalties for unassigned tasks)

Constraints:
- Each implement assigned to at most one task
- Each task assigned to exactly one implement-vehicle pair (or not assigned)
- Each vehicle either assigned or returns to depot
- Battery capacity constraints
- Compatibility constraints between entities

Author: Jorge
Date: 2024
"""

import copy as copy
from gurobipy import *
from gurobipy import GRB
import numpy as np
import pandas as pd
import os

def Optimization (C,M,That,I,K,V,Mmax,Cmax,IK,KI,IV,VI,KV,VK,alpha,beta,b,Cprime,Tmin):
<<<<<<< Updated upstream
    #Model definition
    model = Model('3index-assignment-3')

    Cmax = np.random.randint(0,1,size=len(V))
    for i in V:
        Cmax[i]=max(Cprime[i],np.max(C[:,:,i]))
    #Set model time limit
    timeLimit = 100
    model.setParam('TimeLimit', timeLimit)
    #model.setParam('MIPGap', 0)
    # ------------------------------------ Decision Variables definitions 
    #Decision variables
    x = {(i,k,v):model.addVar(vtype=GRB.BINARY, name="x_" + str(i) + "_" + str(k) + "_" + str(v)) 
                        for i in I for k in K for v in V 
            }
=======
    """
    Create and solve the static assignment optimization model.
    
    Args:
        C (np.array): Cost matrix [num_implements x num_tasks x num_vehicles]
        M (np.array): Penalty vector for each task [num_tasks]
        That (np.array): Current battery level for each vehicle [num_vehicles]
        I (list): List of available implement indices
        K (list): List of available task indices
        V (list): List of available vehicle indices
        Mmax (float): Normalization constant for penalties
        Cmax (np.array): Normalization constants for costs per vehicle [num_vehicles]
        IK, KI, IV, VI, KV, VK (np.array): Compatibility matrices
        alpha (float): Weight for cost component in objective (typically 0.05)
        beta (float): Weight for penalty component in objective (typically 0.95)
        b (np.array): Energy consumption matrix [num_implements x num_tasks x num_vehicles]
        Cprime (np.array): Depot return cost for each vehicle [num_vehicles]
        Tmin (float): Minimum battery threshold
        
    Returns:
        model: Gurobi model object with the solution (if feasible)
    """
    # ===================================
    # Model Initialization
    # ===================================
    model = Model('StaticMRTAI-SinglePeriod')

    # Recalculate normalization constants per vehicle
    Cmax = np.random.randint(0,1,size=len(V))
    for i in V:
        Cmax[i]=max(Cprime[i],np.max(C[:,:,i]))
    
    # Set solver parameters
    timeLimit = 1000  # Maximum solving time in seconds
    model.setParam('TimeLimit', timeLimit)
    #model.setParam('MIPGap', 0)  # Optional: set optimality gap tolerance
    
    # ===================================
    # Decision Variables
    # ===================================
    # x[i,k,v]: Binary variable, 1 if implement i with vehicle v performs task k
    # Only create variables for compatible combinations
    x = {(i, k, v): model.addVar(vtype=GRB.BINARY, name="x_" + str(i) + "_" + str(k) + "_" + str(v)) 
         for i in I for k in K for v in V if IK[i, k] == 1 and IV[i, v] == 1 and VK[v, k] == 1}
>>>>>>> Stashed changes

    # y[k]: Binary variable, 1 if task k is assigned (completed)
    y = {(k): model.addVar(vtype=GRB.BINARY, name="y_" + str(k))
                    for k in K 
            }
    
    # z[v]: Binary variable, 1 if vehicle v returns to depot without task
    z = {(v): model.addVar(vtype=GRB.BINARY, name="z_" + str(v))
                    for v in V 
            }

<<<<<<< Updated upstream
    #Objective function
    obj = (alpha)*(quicksum(((quicksum((C[i][k][v] * x[i, k, v]) for i in I for k in K) + Cprime[v]*z[v])/(Cmax[v])) for v in V)) \
        + (beta/Mmax) * quicksum(M[k] * (1 - y[k]) for k in K)
=======
    # ===================================
    # Objective Function
    # ===================================
    # Minimize: alpha * (normalized assignment costs) + beta * (penalties for unassigned tasks)
    obj = (alpha) * quicksum(
        ((quicksum(C[i][k][v] * x[i, k, v] for (i, k, v) in x if v == vehicle) + Cprime[vehicle] * z[vehicle]) / Cmax[vehicle])
        for vehicle in V
    ) + (beta / Mmax) * quicksum(M[k] * (1 - y[k]) for k in K)
>>>>>>> Stashed changes
    
    model.setObjective(obj, GRB.MINIMIZE)

    # ===================================
    # Constraints
    # ===================================
    
    # Constraint 5: Each implement assigned to at most one task-vehicle pair
    # Each implement can only work on one task at a time
    for i in I:
<<<<<<< Updated upstream
        model.addConstr(quicksum(x[i, k, v] for k in KI[i] for v in VI[i]) <= 1)
=======
        model.addConstr(quicksum(x[i, k, v] for k in K for v in V if IK[i,k]==1 and IV[i,v]==1 and KV[k,v]==1) <= 1,
                       name=f"implement_{i}_single_assignment")
>>>>>>> Stashed changes

    # Constraint 6: Task assignment consistency
    # If task k is assigned (y[k]=1), exactly one implement-vehicle pair must perform it
    for k in K:
<<<<<<< Updated upstream
        model.addConstr(quicksum(x[i, k, v] for i in IK[k] for v in VK[k]) == y[k])
    #Constraints 7: vehicle assignment to depot or task-implement
    for v in V:
        model.addConstr(z[v] + quicksum(x[i, k, v] for i in IV[v] for k in KV[v]) == 1)
    #Constraints 8: vehicle autonomy constraints (could be preprocessed)
    for v in V:
        model.addConstr(quicksum((b[i][k][v]) * x[i, k, v] for i in I for k in K) <= That[v]-Tmin)
=======
        model.addConstr(quicksum(x[i, k, v] for i in I for v in V if IK[i,k]==1 and IV[i,v]==1 and KV[k,v]==1) == y[k],
                       name=f"task_{k}_assignment")
    
    # Constraint 7: Vehicle assignment exclusivity
    # Each vehicle either performs one task or returns to depot
    for v in V:
        model.addConstr(z[v] + quicksum(x[i, k, v] for i in I for k in K if IK[i,k]==1 and IV[i,v]==1 and KV[k,v]==1) == 1,
                       name=f"vehicle_{v}_single_action")
    
    # Constraint 8: Battery/energy capacity constraints
    # Total energy consumption must not exceed available battery minus minimum threshold
    for v in V:
        model.addConstr(quicksum((b[i][k][v]) * x[i, k, v] for i in I for k in K if IK[i,k]==1 and IV[i,v]==1 and KV[k,v]==1) <= That[v]-Tmin,
                       name=f"vehicle_{v}_battery")
>>>>>>> Stashed changes

    # ===================================
    # Solve the Model
    # ===================================
    model.optimize()
<<<<<<< Updated upstream


=======
    model.write("model.lp")  # Write model to file for debugging
>>>>>>> Stashed changes

    return model


################################################################## STATIC INSTANCE ############################################################################################################

# num_periods=1
# set_data = 1
# CostBalance = [1,0]
# EnergyBalance = [1,0]
# GlobalResults = {}
# for k in range (1,2):
#     for i in range(10,21,10):
#         num_implements=5
#         num_tasks=5
#         num_vehicles=5
#         set_data=k
#         os.chdir("Data/Costs")
#         directory_path="Parameters-("+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+","+str(num_periods)+")-"+str(set_data)
#         print("Running optimization for", num_implements, "implements,", num_tasks, "tasks and", num_vehicles, "vehicles.")
        

#         try:
#             os.chdir(directory_path)
#             Cst = np.loadtxt('Cst.csv', delimiter=',', dtype=int).reshape(num_implements, num_tasks, num_vehicles)
#             Cd = np.loadtxt('Cd.csv', delimiter=',', dtype=int).reshape(num_implements, num_tasks, num_vehicles)
#             M = np.loadtxt('M.csv', delimiter=',', dtype=int).reshape(num_tasks)
#             T_max = np.loadtxt('T_max.csv', delimiter=',', dtype=int)
#             That = np.loadtxt('T.csv', delimiter=',', dtype=int)
#             That = np.array(That)
#             bst = np.loadtxt('bst.csv', delimiter=',', dtype=int).reshape(num_implements, num_tasks, num_vehicles)
#             bd = np.loadtxt('bd.csv', delimiter=',', dtype=int).reshape(num_implements, num_tasks, num_vehicles)
#             C=(CostBalance[0]*Cst+CostBalance[1]*Cd).astype(int)
#             b=(EnergyBalance[0]*bst+EnergyBalance[1]*bd).astype(int)
#             Cprime = np.loadtxt('Cprime.csv', delimiter=',', dtype=int).reshape(num_vehicles)
#             print("............................................................")
#             print("Data exists, loading data from files")
#             print("............................................................")

#         except:
#             print("............................................................")
#             print("Data does not exist, creating data and saving to files")
#             print("............................................................")
#             os.makedirs(directory_path)
#             os.chdir(directory_path)
#             np.random.seed(set_data)  
#             Cst = np.random.randint(1, 100, size=(num_implements, num_tasks, num_vehicles))
#             np.random.seed(set_data)  
#             Cd = np.random.randint(1, 100, size=(num_implements, num_tasks, num_vehicles))
#             np.random.seed(set_data)  
#             M = np.random.randint(1, 2000, size=(num_tasks))
#             np.random.seed(set_data)  
#             T_max = np.random.randint(100,200, size=(num_vehicles)) 
#             np.random.seed(set_data)  
#             That = [np.random.randint(0.8*T_max[i], T_max[i]) for i in range(num_vehicles)]
#             np.random.seed(set_data)  
#             That = np.array(That)


#             np.random.seed(set_data) 
#             bst = np.random.randint(1, 20, size=(num_implements, num_tasks, num_vehicles))
#             np.random.seed(set_data)
#             bd = np.random.randint(1, 20, size=(num_implements, num_tasks, num_vehicles))
#             np.random.seed(set_data)
#             Cprime = np.random.randint(1, 100, size=(num_vehicles))       
                                
#             b=(EnergyBalance[0]*bst+EnergyBalance[1]*bd).astype(int)
#             C=(CostBalance[0]*Cst+CostBalance[1]*Cd).astype(int)

#             # Guardar en archivos CSV
#             bst_reshaped = bst.reshape(-1, num_vehicles)
#             bd_reshaped = bd.reshape(-1, num_vehicles)
#             Cprime_reshaped = Cprime.reshape(-1, num_vehicles)
#             Cst_reshaped = Cst.reshape(-1, num_vehicles)
#             Cd_reshaped = Cd.reshape(-1, num_vehicles)
#             M_reshaped = M.reshape(num_periods, -1)
#             T_max_reshaped = T_max.reshape(1, -1)
#             That_reshaped = np.array(That).reshape(1, -1)

#             # Guardar en archivos CSV
#             pd.DataFrame(Cprime_reshaped).to_csv('Cprime.csv', index=False, header=False)
#             pd.DataFrame(bst_reshaped).to_csv('bst.csv', index=False, header=False)
#             pd.DataFrame(bd_reshaped).to_csv('bd.csv', index=False, header=False)
#             pd.DataFrame(Cst_reshaped).to_csv('Cst.csv', index=False, header=False)
#             pd.DataFrame(Cd_reshaped).to_csv('Cd.csv', index=False, header=False)
#             pd.DataFrame(M_reshaped).to_csv('M.csv', index=False, header=False)
#             pd.DataFrame(T_max_reshaped).to_csv('T_max.csv', index=False, header=False)
#             pd.DataFrame(That_reshaped).to_csv('T.csv', index=False, header=False)


#         I=range(num_implements)
#         V=range(num_vehicles)
#         K=range(num_tasks)


#         if num_periods==1:
#             Cmax=1
#             Mmax=sum(M[k] for k in K)
#         else:
#             Cmax=1
#             Mmax=sum(M[0][k] for k in K for t in range(num_periods))

#         KI =[[i for i in range(num_tasks)] for _ in range(num_implements)]
#         IK=[[i for i in range(num_implements)] for _ in range(num_tasks)]
#         IV=[[i for i in range(num_implements)] for _ in range(num_vehicles)]
#         VI=[[i for i in range(num_vehicles)] for _ in range(num_implements)]
#         KV=[[i for i in range(num_tasks)] for _ in range(num_vehicles)]
#         VK=[[i for i in range(num_vehicles)] for _ in range(num_tasks)]
#         alpha,beta,=0.5,0.5
#         gamma=0
#         Tmin=15


#     # print(list)
#     # # # # ###################################################################### RUN MODELS ############################################################################################################

#         modelo=Optimization (C,M,That,I,K,V,Mmax,Cmax,IK,KI,IV,VI,KV,VK,alpha,beta,b,Cprime,Tmin)
#         # model.write("model.lp")
#         # all_vars = model.getVars()
#         # values = model.getAttr("X", all_vars)
#         # names = model.getAttr("VarName", all_vars)  


#         # tot_var = {name: val for name,val in zip(names, values) if val>0}
#         # variables_count = {'x': 0, 'y': 0, 'z': 0}
#         # for key in tot_var:
#         #     if key.startswith('x'):
#         #         variables_count['x'] += 1
#         #     elif key.startswith('y'):
#         #         variables_count['y'] += 1
#         #     elif key.startswith('z'):
#         #         variables_count['z'] += 1
            
#         # print(variables_count)
#         all_vars = modelo.getVars()
#         values = modelo.getAttr("X", all_vars)
#         names = modelo.getAttr("VarName", all_vars)
#         tot_var = {name: val for name,val in zip(names, values) if val>0}
#         print(tot_var)
#         # num_z_values = 0
#         # num_z_values = sum(1 for asignacion in tot_var.keys() if asignacion.startswith('z'))
#         # GlobalResults[str(i)]={"Runtime":modelo.Runtime,"ObjVal":modelo.ObjVal,"MIPGap":modelo.MIPGap,"Robot in the depot":num_z_values}
#         # new_dir = os.path.abspath(os.path.join(os.getcwd(), "../../../"))

#         # # Cambiar el directorio de trabajo
#         # os.chdir(new_dir)

#         # Cambiar el directorio de trabajo
    

#     # df = pd.DataFrame({'Result':GlobalResults.values()})
#     # df.to_csv("ResultDynamic-"+str(k)+".csv", mode='a', header=True, index= False)


