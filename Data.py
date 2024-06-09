import numpy as np
import pandas as pd
import ast
import os
import Compatibility
import inspect


def GeneralgeneratedData(num_implements,num_tasks,num_vehicles,set_data,num_periods):

    np.random.seed(set_data)  
    Cst = np.random.randint(1, 100, size=(num_implements, num_tasks, num_vehicles))
    np.random.seed(set_data+10)  
    Cd = np.random.randint(1, 100, size=(num_implements, num_tasks, num_vehicles))
    np.random.seed(set_data)  
    M = np.random.randint(1, 2000, size=(num_tasks))
    np.random.seed(set_data)  
    T_max = np.random.randint(100,200, size=(num_vehicles)) 
    np.random.seed(set_data)  
    That = [np.random.randint(0.8*T_max[i], T_max[i]) for i in range(num_vehicles)]
    That = np.array(That)

    if num_periods>1:
        Cst_pivot=Cst
        Cd_pivot=Cd
        M_pivot=M

        for _ in range(num_periods-1):
            Cstt = np.random.normal(loc=Cst, scale=1).astype(int)
            Cst_pivot = np.concatenate((Cst_pivot, Cstt))
            Cdt = np.random.normal(loc=Cd, scale=1).astype(int)
            Cd_pivot = np.concatenate((Cd_pivot, Cdt))
            Mt = np.random.normal(loc=M, scale=1).astype(int)
            M_pivot = np.concatenate((M_pivot, Mt))

        Cst=Cst_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)
        Cd=Cd_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)
        M=M_pivot.reshape(num_periods,num_tasks)

    
    return Cst,Cd,M,That,T_max




def CostData(num_implements,num_tasks,num_vehicles,set_data,num_periods,CostBalance):
    os.chdir("Data/Costs/")
    I=range(num_implements)
    V=range(num_vehicles)
    K=range(num_tasks)
    directory_path="Parameters-("+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+","+str(num_periods)+")-"+str(set_data)
    if os.path.exists(directory_path):
        os.chdir(directory_path)
        Cst = np.loadtxt('Cst.csv', delimiter=',', dtype=int).reshape(num_periods,num_implements, num_tasks, num_vehicles)
        Cd = np.loadtxt('Cd.csv', delimiter=',', dtype=int).reshape(num_periods,num_implements, num_tasks, num_vehicles)
        M = np.loadtxt('M.csv', delimiter=',', dtype=int)
        T_max = np.loadtxt('T_max.csv', delimiter=',', dtype=int)
        That = np.loadtxt('T.csv', delimiter=',', dtype=int)

        C=(CostBalance[0]*Cst+CostBalance[1]*Cd).astype(int)
        C_reshaped = C.reshape(-1, num_vehicles)
        pd.DataFrame(C_reshaped).to_csv('C.csv', index=False, header=False)

        if num_periods==1:
            C=C[0]
            Cmax=1
            Mmax=sum(M[k] for k in K)
        else:
            Cmax=1
            Mmax=sum(M[0][k] for k in K for t in range(num_periods))

    else:
        os.makedirs(directory_path)
        os.chdir(directory_path)
        Cst,Cd,M,That,T_max=GeneralgeneratedData(num_implements,num_tasks,num_vehicles,set_data,num_periods)

        Cst_reshaped = Cst.reshape(-1, num_vehicles)
        Cd_reshaped = Cd.reshape(-1, num_vehicles)
        M_reshaped = M.reshape(num_periods, -1)
        T_max_reshaped = T_max.reshape(1, -1)
        That_reshaped = np.array(That).reshape(1, -1)

        # Guardar en archivos CSV
        pd.DataFrame(Cst_reshaped).to_csv('Cst.csv', index=False, header=False)
        pd.DataFrame(Cd_reshaped).to_csv('Cd.csv', index=False, header=False)
        pd.DataFrame(M_reshaped).to_csv('M.csv', index=False, header=False)
        pd.DataFrame(T_max_reshaped).to_csv('T_max.csv', index=False, header=False)
        pd.DataFrame(That_reshaped).to_csv('T.csv', index=False, header=False)


        C=(CostBalance[0]*Cst+CostBalance[1]*Cd).astype(int)

        C=(CostBalance[0]*Cst+CostBalance[1]*Cd).astype(int)
        C_reshaped = C.reshape(-1, num_vehicles)
        pd.DataFrame(C_reshaped).to_csv('C.csv', index=False, header=False)

        if num_periods==1:
            Cmax=1
            Mmax=sum(M[k] for k in K)
        else:
            Cmax=1
            Mmax=sum(M[0][k] for k in K for t in range(num_periods))


    return C, M, That, I, K, V, Mmax, Cmax,T_max

def CompatibilityData(num_implements,num_tasks,num_vehicles,full):
    os.chdir("Data/Compatibility/")
    if full==True:
        KI =[[i for i in range(num_tasks)] for _ in range(num_implements)]
        IK=[[i for i in range(num_implements)] for _ in range(num_tasks)]
        IV=[[i for i in range(num_implements)] for _ in range(num_vehicles)]
        VI=[[i for i in range(num_vehicles)] for _ in range(num_implements)]
        KV=[[i for i in range(num_tasks)] for _ in range(num_vehicles)]
        VK=[[i for i in range(num_vehicles)] for _ in range(num_tasks)]

    else:
        with open("CompData-"+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+".txt", 'r') as file:
            IK=ast.literal_eval(file.readline())
            KI =ast.literal_eval(file.readline())
            # KI,IV,KV,VK=Compatibility.CompleteCompatibility(num_implements,num_tasks,num_vehicles,IK,VI)
            IV=ast.literal_eval(file.readline())
            VI=ast.literal_eval(file.readline())
            KV=ast.literal_eval(file.readline())
            VK=ast.literal_eval(file.readline())
    return IK,KI,IV,VI,KV,VK


def SpecificData(get_model_inputs,set_data,num_vehicles,gamma,num_implements,num_tasks,num_periods,EnergyBalance):
    Specific = {}

    if "gamma" in get_model_inputs:
        Specific["gamma"] = gamma
    if "T_max" in get_model_inputs:
        np.random.seed(set_data) 
        T_max = np.random.randint(100,200, size=(num_vehicles)).astype(int)
        Specific["T_max"] = T_max
    if "Tmax" in get_model_inputs:
        Tmax =sum(T_max[v] for v in range(num_vehicles))
        Specific["Tmax"] = Tmax
    if "b" in get_model_inputs:
        os.chdir("Data/Costs/")
        directory_path="Parameters-("+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+","+str(num_periods)+")-"+str(set_data)
        os.chdir(directory_path)
        try: 
            bst=np.loadtxt('bst.csv', delimiter=',', dtype=int).reshape(num_periods,num_implements, num_tasks, num_vehicles)
            bd=np.loadtxt('bd.csv', delimiter=',', dtype=int).reshape(num_periods,num_implements, num_tasks, num_vehicles)
            if num_periods==1:
                bst = bst[0]
                bd = bd[0]
            b=(EnergyBalance[0]*bst+EnergyBalance[1]*bd).astype(int)
            b_reshaped=b.reshape(-1, num_vehicles)
            pd.DataFrame(b_reshaped).to_csv('b.csv', index=False, header=False)
        except:
            np.random.seed(set_data)
            bst = np.random.randint(1, 20, size=(num_implements, num_tasks, num_vehicles))
            bd = np.random.randint(1, 20, size=(num_implements, num_tasks, num_vehicles))
            if num_periods>1:
                bst_pivot=bst
                bd_pivot=bd

                for _ in range(num_periods-1):
                    bstt = np.random.normal(loc=bst, scale=1).astype(int)
                    bst_pivot = np.concatenate((bst_pivot, bstt))
                    bdt = np.random.normal(loc=bd, scale=1).astype(int)
                    bd_pivot = np.concatenate((bd_pivot, bdt))

                bst=bst_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)
                bd=bd_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)
        
            bst_reshaped = bst.reshape(-1, num_vehicles)
            bd_reshaped = bd.reshape(-1, num_vehicles)

            pd.DataFrame(bst_reshaped).to_csv('bst.csv', index=False, header=False)
            pd.DataFrame(bd_reshaped).to_csv('bd.csv', index=False, header=False)    
            b=(EnergyBalance[0]*bst+EnergyBalance[1]*bd).astype(int)
            b_reshaped=b.reshape(-1, num_vehicles)
            pd.DataFrame(b_reshaped).to_csv('b.csv', index=False, header=False)
        Specific["b"] = b
    if "Tau" in get_model_inputs:
        Tau = range(num_periods)
        Specific["Tau"] = Tau
    if "Vhat" in get_model_inputs:
        Vhat = Ihat = np.ones((num_periods,num_vehicles)).astype(int)
        Specific["Vhat"] = Vhat
    if "Ihat" in get_model_inputs:
        Ihat = np.ones((num_periods,num_implements)).astype(int)
        Specific["Ihat"] = Ihat
    if "Khat" in get_model_inputs:
        Khat = np.ones((num_periods,num_tasks),dtype=int).astype(int)
        Khat[1:num_periods][:]=0
        Specific["Khat"] = Khat
    if "r" in get_model_inputs:
        np.random.seed(set_data)
        r= np.random.randint(20, 100, size=(num_implements, num_tasks))
        Specific["r"] = r
    if "d" in get_model_inputs:
        np.random.seed(set_data)
        d= np.random.randint(1, 30, size=(num_periods,num_tasks))
        Specific["d"] = d
    if "Cprime" in get_model_inputs:
        try:
            Cprime = np.loadtxt('Cprime.csv', delimiter=',', dtype=int).reshape(num_periods,num_vehicles)
            if num_periods==1:
                Cprime = Cprime[0]
        except:
            np.random.seed(set_data+20)
            Cprime = np.random.randint(1, 100, size=(num_periods,num_vehicles))
            Cprime_reshaped = Cprime.reshape(-1, num_vehicles)
            pd.DataFrame(Cprime_reshaped).to_csv('Cprime.csv', index=False, header=False)
            if num_periods==1:
                Cprime = Cprime[0]
        Specific["Cprime"] = Cprime
    if "Tmin" in get_model_inputs:
        Tmin = 15
        Specific["Tmin"] = Tmin
    # if "Cmaxpri" in get_model_inputs:
    #     if num_periods==1:
    #         Cmaxpri = sum(Cprime[v] for v in range(num_vehicles))
    #     else:
    #         Cmaxpri = np.max(Cprime)*num_vehicles
    #     Specific["Cmaxpri"] = Cmaxpri
    return Specific

def PositionData(num_implements,num_tasks,num_vehicles,set_data):

    os.chdir("Data/Positions/")
    directory_path="Positions-("+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+")-"+str(set_data)
    if os.path.exists(directory_path):
        os.chdir(directory_path)
        Implements = np.loadtxt('Implements.csv', delimiter=',',dtype=float).reshape(num_implements,3)
        Tasks = np.loadtxt('Tasks.csv', delimiter=',', dtype=int).reshape(num_tasks,4)
        Vehicles = np.loadtxt('Vehicles.csv', delimiter=',', dtype=float).reshape(num_vehicles,5)
    else:
        os.makedirs(directory_path)
        os.chdir(directory_path)
        np.random.seed(set_data)
        Implements = np.random.randint(0, 100, size=(num_implements,2))
        np.random.seed(set_data)
        EfImplement=  np.random.randint(80, 100, size=(num_implements,1))
        Implements = np.concatenate((Implements,EfImplement/100),axis=1)
        np.random.seed(set_data+10)
        Tasks = np.random.randint(0, 100, size=(num_tasks,3))
        np.random.seed(set_data+12)
        Penalty=  np.random.randint(100, 1000, size=(num_tasks,1))
        Tasks = np.concatenate((Tasks,Penalty),axis=1)
        np.random.seed(set_data+20)
        Vehicles = np.random.randint(0, 100, size=(num_vehicles,2))
        np.random.seed(set_data+20)
        EfVehicle=  np.random.randint(80, 100, size=(num_vehicles,1))
        Vehicles = np.concatenate((Vehicles,EfVehicle/100),axis=1)
        np.random.seed(set_data)  
        T_max = np.random.randint(100,101, size=(num_vehicles)) 
        Vehicles = np.concatenate((Vehicles,T_max.reshape(-1,1)),axis=1)
        np.random.seed(set_data)  
        That = [np.random.randint(0.75*T_max[i], T_max[i]) for i in range(num_vehicles)]
        That = np.array(That)
        Vehicles = np.concatenate((Vehicles,That.reshape(-1,1)),axis=1)

        

        Implements_reshaped = Implements.reshape(-1, 3)
        Tasks_reshaped = Tasks.reshape(-1, 4)
        Vehicles_reshaped = Vehicles.reshape(-1, 5)

        pd.DataFrame(Implements_reshaped).to_csv('Implements.csv', index=False, header=False)
        pd.DataFrame(Tasks_reshaped).to_csv('Tasks.csv', index=False, header=False)
        pd.DataFrame(Vehicles_reshaped).to_csv('Vehicles.csv', index=False, header=False)

    return Implements,Tasks,Vehicles


    
