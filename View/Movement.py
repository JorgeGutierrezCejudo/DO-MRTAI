import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import random
from Tools import Defactorise as tl
import time
import matplotlib

#matplotlib.use('GTK3Agg')

def update_positions(Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, Z_vehicles,Distancia,probability):
    Event = False
    New_task = []
    A_implements, A_tasks, A_vehicles = tl.XAsignmentsDefactorise(Asignments)
    num_vehicles = len(A_vehicles)
    num_vehiclesd = len(Z_vehicles)

    
    reached_info = []  # Lista para almacenar la información de los vehículos que han llegado
    
    for i in range(num_vehicles):
        if not reached_implements[A_vehicles[i]]:
            # Move vehicles towards their respective implements
            dx = Implements[A_implements[i], 0] - Vehicles[A_vehicles[i], 0]
            dy = Implements[A_implements[i], 1] - Vehicles[A_vehicles[i], 1]
            alpha = math.atan2(dy, dx)

            Vehicles[A_vehicles[i], 0] += Vl[i] * math.cos(alpha)
            Vehicles[A_vehicles[i], 1] += Vl[i] * math.sin(alpha)

            Distancia[A_vehicles[i]]+= abs(Vl[i]*math.tan(alpha))


            # Check if the vehicle has reached the implement
            if np.linalg.norm([dx, dy]) < Vl[i]:
                reached_implements[A_vehicles[i]] = True
                Vehicles[A_vehicles[i], 0] = Implements[A_implements[i], 0]
                Vehicles[A_vehicles[i], 1] = Implements[A_implements[i], 1]
        elif not reached_tasks[A_vehicles[i]]:
            # Move combined vehicle and implement towards their respective tasks
            dx = Tasks[A_tasks[i], 0] - Vehicles[A_vehicles[i], 0]
            dy = Tasks[A_tasks[i], 1] - Vehicles[A_vehicles[i], 1]
            alpha = math.atan2(dy, dx)

            Vehicles[A_vehicles[i], 0] += Vl[i] * math.cos(alpha)
            Vehicles[A_vehicles[i], 1] += Vl[i] * math.sin(alpha)
            Implements[A_implements[i], 0] = Vehicles[A_vehicles[i], 0]
            Implements[A_implements[i], 1] = Vehicles[A_vehicles[i], 1]

            Distancia[A_vehicles[i]]+= abs(Vl[i]*math.tan(alpha))

            # Check if the vehicle has reached the task
            if np.linalg.norm([dx, dy]) < Vl[i]:
                reached_tasks[A_vehicles[i]] = True
                Vehicles[A_vehicles[i], 0] = Tasks[A_tasks[i], 0]
                Vehicles[A_vehicles[i], 1] = Tasks[A_tasks[i], 1]
                Implements[A_implements[i], 0] = Tasks[A_tasks[i], 0]
                Implements[A_implements[i], 1] = Tasks[A_tasks[i], 1]
                Event = True
                reached_info.append((A_implements[i], A_tasks[i], A_vehicles[i]))  # Almacenar la información del vehículo, implemento y tarea alcanzados
    for i in range(num_vehiclesd):
        # Move vehicle back to depot
        dx = 1 - Vehicles[Z_vehicles[i], 0]
        dy = 1 - Vehicles[Z_vehicles[i], 1]
        alpha = math.atan2(dy, dx)

        Vehicles[Z_vehicles[i], 0] += Vl[i] * math.cos(alpha)
        Vehicles[Z_vehicles[i], 1] += Vl[i] * math.sin(alpha)
        Distancia[Z_vehicles[i]]+= abs(Vl[i]*math.tan(alpha))
        
        # Check if the vehicle has reached the depot
        if np.linalg.norm([dx, dy]) < Vl[i]:
            Vehicles[Z_vehicles[i], 0] = 1
            Vehicles[Z_vehicles[i], 1] = 1
            #Event = True

    #Check if a new task appear
    if random.random() < probability:
        New_task=NewTasks(1)
        print(New_task)
        Event=True



    return Event, Vehicles, Implements, reached_info, New_task,Distancia

def init_plot(ax, Implements, Tasks, Vehicles):
    ax.clear()
    ax.scatter(Implements[:, 0], Implements[:, 1], marker="^", s=10**2, c="black", label="Implements")
    ax.scatter(Tasks[:, 0], Tasks[:, 1], c="blue", marker="s", alpha=0.3, s=Tasks[:, 2] * 20)
    ax.scatter(Tasks[:, 0], Tasks[:, 1], c="blue", marker="s", label="Tasks", alpha=1)
    ax.scatter(0, 0, marker="s", s=10**2, c="green", label="Depot", alpha=0.4)
    ax.scatter(Vehicles[:, 0], Vehicles[:, 1], marker="H", s=10**2, c="red", label="Vehicles")

    # Add vehicle labels
    for i in range(len(Vehicles)):
        ax.text(Vehicles[i, 0], Vehicles[i, 1], f'V{i}', fontsize=12, ha='right')

    ax.set_title("Allocation Problem")
    ax.legend(loc='upper right')
    ax.set_xlim(-1, 100)
    ax.set_ylim(-1, 100)

def update_plot(ax, Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, Z_vehicles,Distancia,probability):
    ax.clear()
    Event, updated_vehicles, updated_implements, reached_info,New_task,Distancia= update_positions(Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, Z_vehicles,Distancia,probability)
    init_plot(ax, updated_implements, Tasks, updated_vehicles)

    
    A_implements, A_tasks, A_vehicles = tl.XAsignmentsDefactorise(Asignments)
    num_vehicles = len(A_vehicles)
    num_vehiclesd = len(Z_vehicles)

    for i in range(num_vehicles):
        imp_index = A_implements[i]
        task_index = A_tasks[i]
        if not reached_implements[A_vehicles[i]]:
            # Draw arrow from vehicle to implement
            ax.annotate("", xy=(Implements[imp_index, 0], Implements[imp_index, 1]),
                        xytext=(Vehicles[A_vehicles[i], 0], Vehicles[A_vehicles[i], 1]),
                        arrowprops=dict(arrowstyle="->", lw=3, color="orange"))
        elif not reached_tasks[A_vehicles[i]]:
            # Draw arrow from implement to task
            ax.annotate("", xy=(Tasks[task_index, 0], Tasks[task_index, 1]),
                        xytext=(Implements[imp_index, 0], Implements[imp_index, 1]),
                        arrowprops=dict(arrowstyle="->", lw=3, color="green"))
    for i in range(num_vehiclesd):
        ax.annotate("", xy=(0, 0),
                        xytext=(Vehicles[Z_vehicles[i], 0], Vehicles[Z_vehicles[i], 1]),
                        arrowprops=dict(arrowstyle="->", lw=3, color="red"))


    ax.set_title(f"Vehicle Movements - Step Fraction {step_fraction:.2f}")
    return Event, updated_vehicles, updated_implements, reached_info,New_task

def animate_allocation(Implements, Tasks, Vehicles, Asignments, ZAsignments,probability,num_steps=100):
    start_time = time.time()  # Registrar el tiempo de inicio
    fig, ax = plt.subplots(figsize=(10, 6))
    reached_implements = np.full(len(Vehicles), False)
    reached_tasks = np.full(len(Vehicles), False)
    Vl = [1] * len(Vehicles)
    Z_vehicles = tl.ZAsignmentsDefactorise(ZAsignments)
    Distancia=np.ones((len(Vehicles)),dtype=float)
    reached_info_all = []  # Lista para almacenar toda la información de los vehículos que han llegado
    execution_time = None  # Inicializar la variable de tiempo de ejecución

    def animate(i):
        nonlocal execution_time,Tasks  # Para modificar las variables en el ámbito externo
        global Event,New_task
        step_fraction = i / num_steps
        Event, updated_vehicles, updated_implements, reached_info, New_task = update_plot(ax, Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, Z_vehicles,Distancia,probability)
        reached_info_all.extend(reached_info)  # Agregar la información de los vehículos que han llegado en este paso
        if Event :
            if len(New_task) > 0:
                Tasks=np.concatenate((Tasks,New_task),axis=0)
            event_occurred = True
            end_time = time.time()  # Registrar el tiempo de finalización
            execution_time = end_time - start_time  # Calcular el tiempo de ejecución
            ani.event_source.stop()
            # plt.close(fig)

    ani = animation.FuncAnimation(fig, animate, frames=num_steps, interval=100)
    plt.show()

    return Event, Vehicles, Implements, Tasks, reached_info_all, execution_time, Distancia

def NewTasks (num):
    print("New tasks")
    NTasks = np.random.randint(0, 100, size=(num,3))
    Penalty=  np.random.randint(100, 1000, size=(num,1))
    NTasks = np.concatenate((NTasks,Penalty),axis=1)

    return NTasks
