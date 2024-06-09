import copy as copy
from gurobipy import *
from gurobipy import GRB
import numpy as np
import pandas as pd
import os


def Optimization (C,M,That,I,K,V,Mmax,Cmax,IK,KI,IV,VI,KV,VK,alpha,beta,T_max,b,Tau,Vhat,Ihat,Khat,Cprime,Tmin):
    Cmax = np.random.randint(0,1,size=len(V))
    for v in V:
        Cmax[v]=sum(Vhat[t,v]*max(Cprime[t,v],np.max(C[t,:,:,v])) for t in Tau)
      
    #Model definition
    model = Model('3index-assignment-1')
    #Set model time limit
    timeLimit = 1000
    model.setParam('TimeLimit', timeLimit)

    # ------------------------------------ Decision Variables definitions 
    #Decision variables
    x = {(i,k,v,t):model.addVar(vtype=GRB.BINARY, name="x_" + str(i) + "_" + str(k) + "_" + str(v)+ "_" + str(t)) 
                    for i in I for k in K for v in V for t in Tau
            }

    y = {(k,t): model.addVar(vtype=GRB.BINARY, name="y_" + str(k)+ "_" + str(t))
                    for k in K for t in Tau
            }
    z = {(v,t): model.addVar(vtype=GRB.BINARY, name="z_" + str(v)+ "_" + str(t))
                    for v in V for t in Tau
            }
    o = {(k,t):model.addVar(vtype=GRB.BINARY, name="O_" + str(k) + "_" + str(t)) for k in K for t in Tau}

    T = {(v,t):model.addVar(vtype=GRB.CONTINUOUS, name="T_" + str(v) + "_" + str(t)) for v in V for t in Tau}


    #Objective function
    obj =(alpha) * quicksum( ((quicksum(C[t][i][k][v] * x[i, k, v, t] + Cprime[t][v]* z[v,t] for i in I for k in K for t in Tau))/(Cmax[v])) for v in V) \
        + (beta/(Mmax)) * quicksum(M[t][k] * (o[k,t] - y[k,t]) for k in K for t in Tau)

    model.setObjective(obj, GRB.MINIMIZE) 

    #Constraints 31: at most 1 implement for task-vehicle 
    for i in I:
        for t in Tau:
            model.addConstr(quicksum(x[i, k, v,t] for k in KI[i] for v in VI[i]) <= Ihat[t][i])
    
    #Constraints 33: at most 1 task for implement-vehicle
    for k in K:
        for t in Tau:
            model.addConstr(quicksum(x[i, k, v,t] for i in IK[k] for v in VK[k]) == y[k,t])

    #Constraints 32: vehicle assignment to depot or task-implement
    for v in V:
        for t in Tau:
            model.addConstr(z[v,t] + quicksum(x[i, k, v, t] for i in IV[v] for k in KV[v]) == Vhat[t][v])

    for v in V:
        for t in Tau:
            model.addConstr(quicksum((b[t][i][k][v]) * x[i, k, v,t] for i in I for k in K) <= T[v,t]-Tmin)
    #Contrait
    for k in K:
        for t in Tau:
            model.addConstr(y[k,t] <= o[k,t])
    
    #Constraints 34: Task availability the first time
    for k in K:
        model.addConstr(o[k,0] == Khat[0][k])
    
    #Constraints 35: Task availability the rest of the time
    for k in K:
        for t in range(len(Tau) - 1):
            model.addConstr(o[k, t + 1] == o[k, t] - y[k,t] + Khat[t+1][k])

    #Constraints 36: vehicle autonomy at first time
    for v in V:
        model.addConstr(T[v,0] == That[v])

    #Constraints 37: vehicle autonomy the rest of the time inferior limit
    for v in V:
        for t in range(len(Tau) - 1):
            model.addConstr(T[v,t + 1] >= T[v,t] - quicksum((b[t][i][k][v]) * x[i, k, v, t] for i in IV[v] for k in KV[v]))

    #Constraints 38: vehicle autonomy the rest of the time superior limit
    for v in V:
        for t in range(len(Tau) - 1):
            model.addConstr(T[v,t + 1] <= T[v,t] - quicksum((b[t][i][k][v]) * x[i, k, v, t] for i in IV[v] for k in KV[v]) + T_max[v] * z[v,t])

    #Constraints 39: vehicle autonomy relation between 37-38
    for v in V:
        for t in range(len(Tau) - 1):
            model.addConstr(T[v,t + 1] >= T_max[v] * z[v, t])

    #Constraints 40: vehicle autonomy relation between 37-38
    for v in V:
        for t in Tau:
            model.addConstr(T[v,t] >=Tmin)

    for v in V:
        for t in Tau:
            model.addConstr(T[v,t] <= T_max[v])

    #Solving
    model.optimize()



    return model


########################################################### DYNAMIC INSTANCE ############################################################################################################


# CostBalance = [1,0.01]
# EnergyBalance = [1,0.2]
# GlobalResults={}
# num_periods=2
# num_implements=3
# num_tasks=6
# num_vehicles=3
# set_data=1
# os.chdir("Data/Costs")
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

# KI =[[i for i in range(num_tasks)] for _ in range(num_implements)]
# IK=[[i for i in range(num_implements)] for _ in range(num_tasks)]
# IV=[[i for i in range(num_implements)] for _ in range(num_vehicles)]
# VI=[[i for i in range(num_vehicles)] for _ in range(num_implements)]
# KV=[[i for i in range(num_tasks)] for _ in range(num_vehicles)]
# VK=[[i for i in range(num_vehicles)] for _ in range(num_tasks)]
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