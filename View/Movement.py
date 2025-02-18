import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import math
import random
from Tools import Defactorise as tl
import time
import matplotlib
from Events import EventLogger as EVlogger
from Events import Events as EV
import time
matplotlib.use('GTK3Agg')
check = False
paused = False

def toggle_pause(event):
    global paused
    paused = not paused  # Alternar entre pausa y reanudación

def update_positions(Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, Z_vehicles,Distancia,probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA,totalDistancia,num_periods,Z_periodsD,vehicle_states):
    global check
    Event = [False, "", 0]
    Imp=False
    Depot=False
    XActual=Vehicles[:,0]
    YActual=Vehicles[:,1]
    New_task = []
    T=Vehicles[:,4]
    if num_periods<=1:
        A_implements, A_tasks, A_vehicles = tl.XAsignmentsDefactorise(Asignments)
        A_periods=np.zeros((len(A_vehicles)),dtype=int)
    else: 
        A_implements, A_tasks, A_vehicles, A_periods=tl.TEXAsignmentsDefactorise(Asignments)
    
    num_vehicles = len(Vehicles)

    
    reached_info = []  # Lista para almacenar la información de los vehículos que han llegado a la tarea.
    depot_reached_info= [] #Lista para almacenar la informacion de los vehiculos que han llegado al deposito
    for v in range(num_vehicles):
        indice = next((i for i in range(len(A_periods)) if A_periods[i] == vehicle_states[v] and A_vehicles[i] == v),None)
        i = indice 
        if i != None:
            if not reached_implements[A_vehicles[i]]:
                # Move vehicles towards their respective implements
                dx = Implements[A_implements[i], 0] - Vehicles[A_vehicles[i], 0]
                dy = Implements[A_implements[i], 1] - Vehicles[A_vehicles[i], 1]
                alpha = math.atan2(dy, dx)

                Vehicles[A_vehicles[i], 0] += Vl[A_vehicles[i]] * math.cos(alpha)
                Vehicles[A_vehicles[i], 1] += Vl[A_vehicles[i]] * math.sin(alpha)
                distance_moved= Vl[A_vehicles[i]] 
                Distancia[A_vehicles[i]] += distance_moved
                totalDistancia[A_vehicles[i]] += distance_moved


                # Check if the vehicle has reached the implement
                if np.linalg.norm([dx, dy]) < Vl[A_vehicles[i]]:
                    reached_implements[A_vehicles[i]] = True
                    Imp=True
                    dif=np.linalg.norm([dx, dy])
            elif not reached_tasks[A_vehicles[i]]:
                # Move combined vehicle and implement towards their respective tasks
                dx = Tasks[A_tasks[i], 0] - Vehicles[A_vehicles[i], 0]
                dy = Tasks[A_tasks[i], 1] - Vehicles[A_vehicles[i], 1]
                alpha = math.atan2(dy, dx)

                Vehicles[A_vehicles[i], 0] += Vl[A_vehicles[i]] * math.cos(alpha)
                Vehicles[A_vehicles[i], 1] += Vl[A_vehicles[i]] * math.sin(alpha)
                Implements[A_implements[i], 0] = Vehicles[A_vehicles[i], 0]
                Implements[A_implements[i], 1] = Vehicles[A_vehicles[i], 1]

                distance_moved= Vl[A_vehicles[i]] 
                Distancia[A_vehicles[i]] += distance_moved
                totalDistancia[A_vehicles[i]] += distance_moved

                # Check if the vehicle has reached the task
                if np.linalg.norm([dx, dy]) < Vl[A_vehicles[i]]:
                    dif=np.linalg.norm([dx, dy])
                    reached_tasks[A_vehicles[i]] = True
                    Implements[A_implements[i], 0] = Tasks[A_tasks[i], 0]
                    Implements[A_implements[i], 1] = Tasks[A_tasks[i], 1]
                    reached_info.append((A_implements[i], A_tasks[i], A_vehicles[i],int(vehicle_states[A_vehicles[i]])))  # Almacenar la información del vehículo, implemento y tarea alcanzados
                    if num_periods<=1:
                        Event = [True, "Simulation", 1]
                    else:
                        if vehicle_states[A_vehicles[i]]==num_periods: #choose when stop the simulation
                            Event = [True, "Simulation", 1]
                        else:
                            vehicle_states[A_vehicles[i]] = vehicle_states[A_vehicles[i]]+1
                            reached_implements[A_vehicles[i]] = False
                            reached_tasks[A_vehicles[i]] = False
                    
        else:
            # Move vehicle back to depot
            indiceZ = next((i for i in range(len(Z_periodsD)) if Z_periodsD[i] == vehicle_states[v] and Z_vehicles[i] == v), None)
            i=indiceZ
            dx = 1 - Vehicles[Z_vehicles[i], 0]
            dy = 1 - Vehicles[Z_vehicles[i], 1]
            alpha = math.atan2(dy, dx)
            

            Vehicles[Z_vehicles[i], 0] += Vl[Z_vehicles[i]] * math.cos(alpha)
            Vehicles[Z_vehicles[i], 1] += Vl[Z_vehicles[i]] * math.sin(alpha)
            distance_moved = Vl[Z_vehicles[i]]
            Distancia[Z_vehicles[i]]+= distance_moved
            totalDistancia[Z_vehicles[i]]+= distance_moved
            
            StTask=Tasks[:,4]
            K=[k for k, State in enumerate(StTask) if State == 0]

            # Check if the vehicle has reached the depot
            if np.linalg.norm([dx, dy]) < Vl[Z_vehicles[i]]:
                dif=np.linalg.norm([dx, dy])
                Vehicles[Z_vehicles[i], 0] = 1
                Vehicles[Z_vehicles[i], 1] = 1
                if T[Z_vehicles[i]]<10:
                    if num_periods<=1:
                        depot_reached_info.append((Z_vehicles[i],int(vehicle_states[Z_vehicles[i]])))
                        Event = [True, "Simulation", 2]
                    else:
                        if vehicle_states[Z_vehicles[i]]==num_periods-1:
                            depot_reached_info.append((Z_vehicles[i],int(vehicle_states[Z_vehicles[i]])))
                            Event = [True, "Simulation", 2]
                        else:
                            vehicle_states[Z_vehicles[i]] = vehicle_states[Z_vehicles[i]]+1
        if check:
            check=False
            if random.random() < probabilityTA:
                Event=[True,"Task",1]
            #Check if a task Disappear
            elif random.random() < probabilityTD:
                Event=[True,"Task",2]
            #Check if a new vehicle Appear
            elif random.random() < probabilityVA:
                Event=[True,"Vehicle",1]
            #Check if a vehicle Disappear
            elif random.random() < probabilityVD:
                Event=[True,"Vehicle",2]
            #Check if a new implement Appear
            elif random.random() < probabilityIA:
                Event=[True,"Implement",1]
            #Check if a implement Disappear
            elif random.random() < probabilityID:
                Event=[True,"Implement",2]


    if Event[0] or Imp:
        for v in range(num_vehicles):
            Distancia[v]=Distancia[v]-Vl[v]+dif
            dx=XActual[v]-Vehicles[v,0]
            dy=YActual[v]-Vehicles[v,1]
            alpha=math.atan2(dy,dx)
            Vehicles[v,1]-=Vl[v]*math.sin(alpha)+dif*math.sin(alpha)
            Vehicles[v,0]-=Vl[v]*math.cos(alpha)+dif*math.cos(alpha)
        Imp=False

            
    return Event, Vehicles, Implements, reached_info,depot_reached_info, New_task,Distancia,totalDistancia,vehicle_states

def init_plot(ax, Implements, Tasks, Vehicles):
    ax.clear()
    
    ax.scatter(Implements[:, 0], Implements[:, 1], marker="^", s=10**2, c="black", label="Implements")

    for i in range(len(Tasks)):
        if Tasks[i, -1] == 0:
            ax.scatter(Tasks[i, 0], Tasks[i, 1], c="blue", marker="s", alpha=0.3, s=Tasks[i, 2] * 20)
            ax.scatter(Tasks[i, 0], Tasks[i, 1], c="blue", marker="s", alpha=1, s=20, label="Task Available" if i == 0 else "")
        else:
            ax.scatter(Tasks[i, 0], Tasks[i, 1], c="red", marker="s", alpha=0.3, s=Tasks[i, 2] * 20 )
            ax.scatter(Tasks[i, 0], Tasks[i, 1], c="red", marker="s", alpha=1, s=20, label="Task Not Available" if i == 1 else "")

    ax.scatter(0, 0, marker="s", s=10**2, c="green", label="Depot", alpha=0.4)
    ax.scatter(Vehicles[:, 0], Vehicles[:, 1], marker="H", s=10**2, c="red", label="Vehicles")

    for i in range(len(Vehicles)):
        ax.text(Vehicles[i, 0], Vehicles[i, 1], f'V{i}', fontsize=12, ha='right')

    ax.set_title("Allocation Problem")
    ax.legend(loc='upper right')
    ax.set_xlim(-1, 100)
    ax.set_ylim(-1, 100)


def update_plot(ax, Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, Z_vehicles, Distancia, probabilityTA, probabilityTD, probabilityVA, probabilityVD, probabilityID, probabilityIA,totalDistancia,num_periods,Z_periodsD,vehicle_states):
    ax.clear()
    
    Event, updated_vehicles, updated_implements, reached_info,depot_reached_info, New_task, Distancia,totalDistancia,vehicle_states = update_positions(Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, Z_vehicles, Distancia, probabilityTA, probabilityTD, probabilityVA, probabilityVD, probabilityID, probabilityIA,totalDistancia,num_periods,Z_periodsD,vehicle_states)

    init_plot(ax, updated_implements, Tasks, updated_vehicles)

    if num_periods<=1:
        A_implements, A_tasks, A_vehicles = tl.XAsignmentsDefactorise(Asignments)
        A_periods=np.zeros((len(A_vehicles)),dtype=int)
    else: 
        A_implements, A_tasks, A_vehicles, A_periods=tl.TEXAsignmentsDefactorise(Asignments)
    
    num_vehicles = len(Vehicles)

    for v in range(num_vehicles):
        indice = next((i for i in range(len(A_periods)) if A_periods[i] == vehicle_states[v] and A_vehicles[i] == v),None)
        i = indice
        if i != None:
            if not reached_implements[A_vehicles[i]]:
                ax.annotate("", xy=(Implements[A_implements[i], 0], Implements[A_implements[i], 1]),
                            xytext=(Vehicles[A_vehicles[i], 0], Vehicles[A_vehicles[i], 1]),
                            arrowprops=dict(arrowstyle="->", lw=3, color="orange"))
            elif not reached_tasks[A_vehicles[i]]:
                ax.annotate("", xy=(Tasks[A_tasks[i], 0], Tasks[A_tasks[i], 1]),
                            xytext=(Vehicles[A_vehicles[i], 0], Vehicles[A_vehicles[i], 1]),
                            arrowprops=dict(arrowstyle="->", lw=3, color="green"))
        else:
            indiceZ = next((i for i in range(len(Z_periodsD)) if Z_periodsD[i] == vehicle_states[v] and Z_vehicles[i] == v), None)
            ax.annotate("", xy=(0, 0),
                        xytext=(Vehicles[Z_vehicles[indiceZ], 0], Vehicles[Z_vehicles[indiceZ], 1]),
                        arrowprops=dict(arrowstyle="->", lw=3, color="red"))
    ax.set_title(f"Vehicle Movements - Step Fraction {step_fraction:.3f}")
    return Event, updated_vehicles, updated_implements, reached_info,depot_reached_info , New_task,totalDistancia,vehicle_states


def custom_animation(Implements, Tasks, Vehicles, Asignments, ZAsignments, probabilityTA, probabilityTD, probabilityVA, probabilityVD, probabilityID, probabilityIA, jota, totalDistancia, num_periods, num_steps=100):
    global check, paused
    start_time = time.time()
    fig, ax = plt.subplots(figsize=(10, 6))
    reached_implements = np.full(len(Vehicles), False)
    reached_tasks = np.full(len(Vehicles), False)
    Vl = np.round(np.random.uniform(1, 1, len(Vehicles)), 0)
    Distancia = np.ones((len(Vehicles)), dtype=float)
    vehicle_states = np.zeros(len(Vehicles))
    reached_info_all = []
    depot_reached_info_all = []
    execution_time = None

    if num_periods <= 1:
        Z_vehicles = tl.ZAsignmentsDefactorise(ZAsignments)
        Z_periodsD = np.zeros((len(Z_vehicles)), dtype=int)
    else:
        Z_vehicles, Z_periodsD = tl.TEZAsignmentsDefactorise(ZAsignments)

    def update_frame(step_fraction,totalDistancia,vehicle_states):
        global Event, New_task, check, paused
        if paused:
            return
        
        # Actualiza la gráfica y obtén los eventos
        Event, updated_vehicles, updated_implements, reached_info, depot_reached_info, New_task, totalDistancia, vehicle_states = update_plot(
            ax, Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks,
            Z_vehicles, Distancia, probabilityTA, probabilityTD, probabilityVA, probabilityVD, probabilityID,
            probabilityIA, totalDistancia, num_periods, Z_periodsD, vehicle_states
        )

        # Almacenar la información de los vehículos que han llegado
        reached_info_all.extend(reached_info)
        depot_reached_info_all.extend(depot_reached_info)

        # Verificar si hay eventos para detener la simulación
        if Event[0]:
            print("***************************************************************************************************************")
            print("                                 EVENT TRIGGERED - SIMULATION STOPPED")
            print("***************************************************************************************************************")
            end_time = time.time()
            execution_time = end_time - start_time
            plt.close(fig)
            return False,execution_time  # Indica que la animación debe detenerse
        
        return True,None

    def run_animation(jota,totalDistancia,vehicle_states):
        i = 0
        stop=True
        while stop:
            step_fraction = ((i + 1) / num_steps) + jota
            stop,execution_time=update_frame(step_fraction,totalDistancia,vehicle_states)
            plt.pause(0.001)
            i += 1
            if i == num_steps:
                jota += 1
                check = True
                i = 0

        return execution_time

    ax_pause = plt.axes([0.45, 0.01, 0.1, 0.05])
    btn_pause = Button(ax_pause, "Pausa")
    btn_pause.on_clicked(toggle_pause)
    
    execution_time=run_animation(jota,totalDistancia,vehicle_states)

    return Event, Vehicles, Implements, Tasks, reached_info_all, depot_reached_info_all, execution_time, Distancia, totalDistancia

