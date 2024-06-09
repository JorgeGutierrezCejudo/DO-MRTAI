import numpy as np
import matplotlib.pyplot as plt
import random


def plot_start(ax, num_implements, num_tasks, num_vehicles, Implements, Tasks, Vehicles, M,period,TAsignments,num_periods):
    xImplement = Implements[:, 0]
    yImplement = Implements[:, 1]
    EfImplement = Implements[:, 2]
    xTask = Tasks[:, 0]
    yTask = Tasks[:, 1]
    Atask = Tasks[:, 2]
    xVehicle = Vehicles[:, 0]
    yVehicle = Vehicles[:, 1]
    EfVehicle = Vehicles[:, 2]
    Tinfo=np.zeros((num_vehicles,num_periods))
    for clave, valor in TAsignments.items():
        partes = clave.split('_')
        i = int(partes[1])
        j = int(partes[2])
        Tinfo[i, j] =int(valor)



    

    ax.scatter(xImplement, yImplement, marker="^", s=10**2, c="black", label="Implements")
    ax.scatter(xTask, yTask, c="blue", marker="s", alpha=0.3, s=Atask*20)
    ax.scatter(xTask, yTask, c="blue", marker="s", label="Tasks", alpha=1)
    ax.scatter(0, 0, marker="s", s=10**2, c="green", label="Depot", alpha=0.4)
    ax.scatter(xVehicle, yVehicle, marker="H", s=10**2, c="red", label="Vehicles")
    
    for i in range(num_implements):
        ax.text(xImplement[i]-1, yImplement[i]-1, f'{i}\nEf: {EfImplement[i]}', fontsize=8, ha='right', color='black', fontweight="bold")
    for i in range(num_tasks):
        ax.text(xTask[i]-1.5, yTask[i]-1.5, f'{i}\nP: {M[period][i]}\nA: {Atask[i]}', fontsize=8, ha='right', color='blue', fontweight="bold")
    for i in range(num_vehicles):
        ax.text(xVehicle[i]-1.5, yVehicle[i]-1.5, f'{i}\nT: {Tinfo[i,period]}\nEf: {EfVehicle[i]}', fontsize=8, ha='right', color='red', fontweight="bold")

    ax.set_title("Allocation Problem")
    ax.legend(loc='upper right')

def plot_finish(ax, num_implements, num_tasks, num_vehicles, Implements, Tasks, Vehicles, Asignments, period,ZAsignments):
    xImplement = Implements[:, 0]
    yImplement = Implements[:, 1]
    xTask = Tasks[:, 0]
    yTask = Tasks[:, 1]
    Atask = Tasks[:, 2]
    xVehicle = Vehicles[:, 0]
    yVehicle = Vehicles[:, 1]

    ax.scatter(xImplement, yImplement, marker="^", s=10**2, c="black", label="Implements")
    ax.scatter(xTask, yTask, c="blue", marker="s", alpha=0.3, s=Atask*20)
    ax.scatter(xTask, yTask, c="blue", marker="s", label="Tasks", alpha=1)
    ax.scatter(0, 0, marker="s", s=10**2, c="green", label="Depot", alpha=0.4)
    ax.scatter(xVehicle, yVehicle, marker="H", s=10**2, c="red", label="Vehicles")

    for i in range(num_implements):
        ax.text(xImplement[i]-0.5, yImplement[i]-0.5, f'{i}', fontsize=12, ha='right', color='black', fontweight="bold")
    for i in range(num_tasks):
        ax.text(xTask[i]-0.5, yTask[i]-0.5, f'{i}', fontsize=12, ha='right', color='blue', fontweight="bold")
    for i in range(num_vehicles):
        ax.text(xVehicle[i]-0.5, yVehicle[i]-0.5, f'{i}', fontsize=12, ha='right', color='red', fontweight="bold")

    A_implements = []
    A_tasks = []
    A_vehicles = []
    A_periods = []
    A_vehiclesD=[]
    A_periodsD=[]
    for key, value in Asignments.items():
        _, i, j, k, t = key.split('_')
        if int(t) == period:
            A_implements.append(int(i))
            A_tasks.append(int(j))
            A_vehicles.append(int(k))
            A_periods.append(int(t))
    if ZAsignments:
        for key, value in ZAsignments.items():
            _, v , t = key.split('_')
            A_vehiclesD.append(int(v))
            A_periodsD.append(int(t))
        for i in range(len(A_vehiclesD)):
            if A_periodsD[i]==period:
                ax.annotate("", xy=(0, 0), xytext=(xVehicle[A_vehiclesD[i]], yVehicle[A_vehiclesD[i]]),
                                arrowprops=dict(arrowstyle="->", lw=3, color="darkorange"))

    for i in range(len(A_implements)):
        ax.annotate("", xy=(xTask[A_tasks[i]], yTask[A_tasks[i]]), xytext=(xImplement[A_implements[i]], yImplement[A_implements[i]]),
                    arrowprops=dict(arrowstyle="->", lw=3, color=colors[A_vehicles[i]]))
    for i in range(len(A_implements)):
        ax.annotate("", xy=(xImplement[A_implements[i]], yImplement[A_implements[i]]), xytext=(xVehicle[A_vehicles[i]], yVehicle[A_vehicles[i]]),
                    arrowprops=dict(arrowstyle="->", lw=3, color=colors[A_vehicles[i]]))


    ax.set_title(f"Results of the Allocation Problem - Period {period}")
    #ax.legend(loc='upper right',)


def init(num_implements, num_tasks, num_vehicles, Implements, Tasks, Vehicles, Asignments, M, num_periods,ZAsignments,TAsignments):
    global colors
    random.seed(1)
    colors = [(random.random(), random.random(), random.random()) for _ in range(num_vehicles)]
    fig, axes = plt.subplots(num_periods, 2, figsize=(14, 7 * num_periods))

    for period in range(num_periods):
        plot_start(axes[period, 0], num_implements, num_tasks, num_vehicles, Implements, Tasks, Vehicles, M,period,TAsignments,num_periods)
        plot_finish(axes[period, 1], num_implements, num_tasks, num_vehicles, Implements, Tasks, Vehicles, Asignments, period,ZAsignments)

        

    plt.tight_layout()

