import copy as copy
from pyscipopt import Model as Modelo
import numpy as np
import pandas as pd
import os

def Optimization (C,M,That,I,K,V,Mmax,Cmax,IK,KI,IV,VI,KV,VK,alpha,beta,b,Cprime,Tmin):
    #Model definition
    model = Modelo('3index-assignment-3')
    model.setParam("display/verblevel", 0)
    #Set model time limit
    timeLimit = 100
    # ------------------------------------ Decision Variables definitions 
    #Decision variables
    x = {(i,k,v):model.addVar(vtype="B", name="x_" + str(i) + "_" + str(k) + "_" + str(v)) 
                        for i in I for k in K for v in V 
            }

    y = {(k): model.addVar(vtype="B", name="y_" + str(k))
                    for k in K 
            }
    
    z = {(v): model.addVar(vtype="B", name="z_" + str(v))
                    for v in V 
            }

    #Objective function
    obj = sum(Cprime[v]* z[v]+ sum(C[i][k][v] * x[i, k, v] for i in I for k in K ) for v in V) + sum(M[k] *(1-y[k])for k in K)
    
    model.setObjective(obj, "minimize")
    print(VI)
    #Constraints 5: at most 1 implement for task-vehicle 
    for i in I:
        model.addCons(sum(x[i, k, v] for k in KI[i] for v in VI[i]) <= 1)

    #Constraints 6: at most 1 task for implement-vehicle
    for k in K:
        model.addCons(sum(x[i, k, v] for i in IK[k] for v in VK[k]) == y[k])
    #Constraints 7: vehicle assignment to depot or task-implement
    for v in V:
        model.addCons(z[v] + sum(x[i, k, v] for i in IV[v] for k in KV[v]) == 1)
    #Constraints 8: vehicle autonomy constraints (could be preprocessed)
    for v in V:
        model.addCons(sum((b[i][k][v]) * x[i, k, v] for i in I for k in K) <= That[v]-Tmin)


    #Solving
    model.optimize()


    return model


################################################################# STATIC INSTANCE ############################################################################################################

# num_periods=1
# set_data = 1
# CostBalance = [1,0]
# EnergyBalance = [1,0]
# GlobalResults = {}
# for k in range (1,2):
#     for i in range(10,21,10):
#         num_implements=40
#         num_tasks=40
#         num_vehicles=40
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
#         # all_vars = modelo.getVars()
#         # values = modelo.getAttr("X", all_vars)
#         # names = modelo.getAttr("VarName", all_vars)
#         # tot_var = {name: val for name,val in zip(names, values) if val>0}
#         # print(tot_var)
#         # num_z_values = 0
#         # num_z_values = sum(1 for asignacion in tot_var.keys() if asignacion.startswith('z'))
#         # GlobalResults[str(i)]={"Runtime":modelo.Runtime,"ObjVal":modelo.ObjVal,"MIPGap":modelo.MIPGap,"Robot in the depot":num_z_values}
#         # new_dir = os.path.abspath(os.path.join(os.getcwd(), "../../../"))

#         # # Cambiar el directorio de trabajo
#         # os.chdir(new_dir)

#         # Cambiar el directorio de trabajo
    

#     # df = pd.DataFrame({'Result':GlobalResults.values()})
#     # df.to_csv("ResultDynamic-"+str(k)+".csv", mode='a', header=True, index= False)


