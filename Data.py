import numpy as np
import pandas as pd
import os

def CalculateCompMatrices (IK,IV):
    # Calculate VK (compatibility between vehicle and task)
    VK = (np.dot(IV.T, IK) > 0).astype(int)

    # Calculate KV (transpose of VK)
    KV = VK.T

    # Calculate KI (transpose of IK)
    KI = IK.T

    # Calculate VI (transpose of IV)
    VI = IV.T

    return VK,KV,VI,KI
    
    

def CompatibilityData(num_implements,num_tasks,num_vehicles,full,set_data):
    os.chdir("Data/Compatibility/")
    directory_path="Compatibility-("+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+")"
    if full==True:        
        IV = np.ones((num_implements, num_vehicles)) 
        IK = np.ones((num_implements, num_tasks)) 
        VK,KV,VI,KI=CalculateCompMatrices(IK,IV)

    else:
        if os.path.exists(directory_path):

            os.chdir(directory_path)
            IK=np.loadtxt('IK.csv', delimiter=',', dtype=int)
            IV =np.loadtxt('IV.csv', delimiter=',', dtype=int)        
            VK,KV,VI,KI=CalculateCompMatrices(IK,IV)

        else:
            np.random.seed(set_data)
            IK = np.random.randint(0, 2, size=(num_implements, num_tasks))  # Implements x Tasks
            IV = np.random.randint(1, 2, size=(num_implements, num_vehicles))  # Implements x Vehicles
            os.makedirs(directory_path)
            os.chdir(directory_path)
            VK,KV,VI,KI=CalculateCompMatrices(IK,IV)
            pd.DataFrame(IK).to_csv('IK.csv', index=False, header=False)
            pd.DataFrame(IV).to_csv('IV.csv', index=False, header=False)
            pd.DataFrame(VK).to_csv('VK.csv', index=False, header=False)




    return IK,KI,IV,VI,KV,VK

def PositionData(num_implements,num_tasks,num_vehicles,set_data):

    os.chdir("Data/Positions/")
    directory_path="Positions-("+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+")-"+str(set_data)
    if os.path.exists(directory_path):
        os.chdir(directory_path)
        Implements = np.loadtxt('Implements.csv', delimiter=',',dtype=float).reshape(num_implements,4)
        Tasks = np.loadtxt('Tasks.csv', delimiter=',', dtype=float).reshape(num_tasks,5)
        Vehicles = np.loadtxt('Vehicles.csv', delimiter=',', dtype=float).reshape(num_vehicles,6)
    else:
        os.makedirs(directory_path)
        os.chdir(directory_path)
        np.random.seed(set_data)
        Implements = np.random.randint(0, 100, size=(num_implements,2))
        np.random.seed(set_data)
        EfImplement=  np.random.randint(80, 100, size=(num_implements,1))
        StImplement=np.zeros((num_implements))
        Implements = np.concatenate((Implements,EfImplement/100),axis=1)
        Implements = np.concatenate((Implements,StImplement.reshape(-1,1)),axis=1)
        np.random.seed(set_data+10)
        Tasks = np.random.randint(0, 100, size=(num_tasks,3))
        np.random.seed(set_data+12)
        Penalty=  np.random.randint(100, 1000, size=(num_tasks,1))
        Tasks = np.concatenate((Tasks,Penalty),axis=1)
        StTask=np.zeros((num_tasks))
        Tasks = np.concatenate((Tasks,StTask.reshape(-1,1)),axis=1)
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
        StVehicle=np.zeros((num_vehicles))
        Vehicles = np.concatenate((Vehicles,StVehicle.reshape(-1,1)),axis=1)

        

        Implements_reshaped = Implements.reshape(-1, 4)
        Tasks_reshaped = Tasks.reshape(-1, 5)
        Vehicles_reshaped = Vehicles.reshape(-1, 6)

        pd.DataFrame(Implements_reshaped).to_csv('Implements.csv', index=False, header=False)
        pd.DataFrame(Tasks_reshaped).to_csv('Tasks.csv', index=False, header=False)
        pd.DataFrame(Vehicles_reshaped).to_csv('Vehicles.csv', index=False, header=False)

    return Implements,Tasks,Vehicles


    
