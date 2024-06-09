from math import sqrt
import numpy as np

def DynamicCalculation(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles):
    xImplement=Implements[:,0]
    yImplement=Implements[:,1]
    xTask=Tasks[:,0]
    yTask=Tasks[:,1]
    xVehicle=Vehicles[:,0]
    yVehicle=Vehicles[:,1]
    Cd=np.zeros((num_implements,num_tasks,num_vehicles))
    Bd=np.zeros((num_implements,num_tasks,num_vehicles))


    for i in range(num_implements):
        for k in range (num_tasks):
            for v in range(num_vehicles):
                Xdiv=abs(xImplement[i]-xVehicle[v])
                Ydiv=abs(yImplement[i]-yVehicle[v])
                Distance1=sqrt(Xdiv**2+Ydiv**2)
                Xdik=abs(xTask[k]-xImplement[v])
                Ydik=abs(yTask[k]-yImplement[v])
                Distance2=sqrt(Xdik**2+Ydik**2)
                Bd[i,k,v]=0.2*((Distance1+Distance2))
                Cd[i,k,v]=0.5*Distance1+0.5*Distance2
    return Cd,Bd

def StaticCalculation(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles):
    aTasck=Tasks[:,2]
    EfImplement=Implements[:,2]
    EfVehicle=Vehicles[:,2]
    Cst=np.zeros((num_implements,num_tasks,num_vehicles))
    Bst=np.zeros((num_implements,num_tasks,num_vehicles))

    for i in range(num_implements):
        for k in range (num_tasks):
            for v in range(num_vehicles):
                Cst[i,k,v]=(aTasck[k]/(EfImplement[i]*EfVehicle[v]))
                Bst[i,k,v]=0.2*Cst[i,k,v]
    return Cst,Bst

def PrimeCalculation(num_implements,num_tasks,num_vehicles,Implements,Tasks,Vehicles):
    xVehicle=Vehicles[:,0]
    yVehicle=Vehicles[:,1]

    Cprime=np.zeros((num_vehicles))

    for v in range(num_vehicles):
        Xd=abs(xVehicle[v]-0)
        Yd=abs(yVehicle[v]-0)
        Distance=sqrt(Xd**2+Yd**2)
        Cprime[v]=Distance
    return Cprime

def NormalicedCalculation(num_periods,M,K):
    if num_periods<=1:
        Cmax=1
        Mmax=sum(M[k] for k in K)
    else:
        Cmax=1
        Mmax=sum(M[0][k] for k in K for t in range(num_periods))

    return Cmax,Mmax

def TimeExtendCalculation (num_periods,num_implements,num_tasks,num_vehicles,Cst,Cd,bst,bd,M,Cprime,Tasks):
    
    Cst_pivot=Cst
    Cd_pivot=Cd
    M_pivot=M
    bst_pivot=bst
    Cprime_pivot=Cprime
    bd_pivot=bd





    #Dynamic calculation of the energy consumption take account the worst case scenario
    
    # MayorCost=np.zeros((num_periods,num_implements,num_vehicles))

    # for t in range(num_periods-1):
    #     MayorCost=np.zeros((num_implements,num_vehicles))
    #     bdt=np.zeros((num_implements,num_tasks,num_vehicles))
    #     for i in range(num_implements):
    #         for v in range (num_vehicles):
    #             for k in range(num_tasks):
    #                 if bd_pivot[i,k,v]==max(bd_pivot[i,:,v]):
    #                     MayorCost[i,v]=int(k)
        
    #     xTask=Tasks[:,0]
    #     yTask=Tasks[:,1]
    #     XPosition=np.zeros((num_implements,num_vehicles))
    #     YPosition=np.zeros((num_implements,num_vehicles))
    #     for i in range(num_implements):
    #         for v in range(num_vehicles):
    #             XPosition[i,v]=xTask[int(MayorCost[i,v])]
    #             YPosition[i,v]=yTask[int(MayorCost[i,v])]

    #     for i in range(num_implements):
    #         for k in range (num_tasks):
    #             for v in range(num_vehicles):
    #                 Xdivk=abs(xTask[k]-XPosition[i,v])
    #                 Ydivk=abs(yTask[k]-YPosition[i,v])
    #                 Distance2=sqrt(Xdivk**2+Ydivk**2)
    #                 bdt[i,k,v]=int(0.2*((Distance2))+bd_pivot[i,k,v])
    #     bd=np.concatenate((bd,bdt)).astype(int)
    #     bd_pivot=bdt

        
        
       
    


                
    for _ in range(num_periods-1):
        Cstt = np.random.normal(loc=Cst, scale=1).astype(int)
        Cst_pivot = np.concatenate((Cst_pivot, Cstt))
        Cdt = np.random.normal(loc=Cd, scale=1).astype(int)
        Cd_pivot = np.concatenate((Cd_pivot, Cdt))
        Mt = np.random.normal(loc=M, scale=1).astype(int)
        M_pivot = np.concatenate((M_pivot, Mt))
        bstt = np.random.normal(loc=bst, scale=1).astype(int)
        bst_pivot = np.concatenate((bst_pivot, bstt))
        bdt = np.random.normal(loc=bd, scale=1).astype(int)
        bd_pivot = np.concatenate((bd_pivot, bdt))
        Cprimet = np.random.normal(loc=Cprime, scale=1).astype(int)
        Cprime_pivot = np.concatenate((Cprime_pivot, Cprimet))
    


    Cst=Cst_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)
    Cd=Cd_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)
    Cprime=Cprime_pivot.reshape(num_periods,num_vehicles)
    M=M_pivot.reshape(num_periods,num_tasks)
    bst=bst_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)
    bd=bd_pivot.reshape(num_periods,num_implements,num_tasks,num_vehicles)


    
    return Cst,Cd,bst,bd,M,Cprime
    