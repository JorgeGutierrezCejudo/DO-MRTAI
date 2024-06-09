import numpy as np


def UpdateInfoST(Asignments,Implements,Tasks,Vehicles,M,That,b,ZAsignments,Tmax):
    A_implements = []
    A_tasks = []
    A_vehicles = []
    A_vehiclesd = []

    for key, value in Asignments.items():
        _, i, j, k = key.split('_')
        A_implements.append(int(i))
        A_tasks.append(int(j))
        A_vehicles.append(int(k))
    if ZAsignments:
        for key, value in ZAsignments.items():
            _, i = key.split('_')
            A_vehiclesd.append(int(i))
        for i in range(len(A_vehiclesd)):
            That[A_vehiclesd[i]]=Tmax[A_vehiclesd[i]]
            Vehicles[A_vehiclesd[i],1]=0
            Vehicles[A_vehiclesd[i],0]=0

#Update the position of the Implements,Tasks and Vehicles
    for i in range(len(A_tasks)):
        Implements[A_implements[i],1]=Tasks[A_tasks[i],1]
        Vehicles[A_vehicles[i],1]=Tasks[A_tasks[i],1]
        Implements[A_implements[i],0]=Tasks[A_tasks[i],0]
        Vehicles[A_vehicles[i],0]=Tasks[A_tasks[i],0]
    for v in range(len(A_tasks)):
        That[A_vehicles[v]]=That[A_vehicles[v]]-b[A_implements[v],A_tasks[v],A_vehicles[v]]


    A_tasks=sorted(A_tasks,reverse=True)
    for i in range(len(A_tasks)):
        Tasks=np.delete(Tasks,A_tasks[i],axis=0)
        M=np.delete(M,A_tasks[i])



    return Implements,Tasks,Vehicles,M,That

def UpdateInfoTE(Asignments,Implements,Tasks,Vehicles,M,That,num_periods,ZAsignments,b,Tmax,TAsignments,num_vehicles):
    A_implements = []
    A_tasks = []
    A_vehicles = []
    A_periods = []
    A_vehiclesd = []
    A_periodsD = []


    for key, value in Asignments.items():
        _, i, j, k ,t= key.split('_')
        A_implements.append(int(i))
        A_tasks.append(int(j))
        A_vehicles.append(int(k))
        A_periods.append(int(t))

#Update the position of the Implements,Tasks and Vehicles
    for i in range(len(A_tasks)):
        if A_periods[i]==max(A_periods):
            Implements[A_implements[i],1]=Tasks[A_tasks[i],1]
            Vehicles[A_vehicles[i],1]=Tasks[A_tasks[i],1]
            Implements[A_implements[i],0]=Tasks[A_tasks[i],0]
            Vehicles[A_vehicles[i],0]=Tasks[A_tasks[i],0]

    if ZAsignments:
        for key, value in ZAsignments.items():
            _, i ,t = key.split('_')
            A_vehiclesd.append(int(i))
            A_periodsD.append(int(t))
        for i in range(len(A_vehiclesd)):
            if A_periodsD[i]==num_periods-1:
                That[A_vehiclesd[i]]=Tmax[A_vehiclesd[i]]
                Vehicles[A_vehiclesd[i],1]=1
                Vehicles[A_vehiclesd[i],0]=1
    

    Tinfo=np.zeros((num_vehicles,num_periods))
    for clave, valor in TAsignments.items():
        partes = clave.split('_')
        i = int(partes[1])
        j = int(partes[2])
        Tinfo[i, j] =int(valor)


    for v in range(len(A_tasks)):
        if A_periods[v]==num_periods-1:
            That[A_vehicles[v]]=Tinfo[A_vehicles[v],num_periods-1]-b[num_periods-1,A_implements[v],A_tasks[v],A_vehicles[v]]

        
    A_tasks=sorted(A_tasks,reverse=True)
    for i in range(len(A_tasks)):
        Tasks=np.delete(Tasks,A_tasks[i],axis=0)
        M=Tasks[:,3]
    

       


    return Implements,Tasks,Vehicles,M,That
    

    
    

    
