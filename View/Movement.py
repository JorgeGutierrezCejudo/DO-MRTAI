"""
Movement.py - Animated Simulation and Visualization for D-MRTAI

This module provides real-time animated visualization of vehicle movements executing
the optimized task assignments. It simulates vehicle trajectories, tracks progress,
and can trigger dynamic events during execution.

Key Features:
- Real-time matplotlib animation of vehicle movements
- Three-phase movement: vehicle to implement to task
- Dynamic event generation during simulation
- Progress tracking and distance measurement
- Pause/resume functionality
- Arrows showing vehicle directions and assignments

Main Functions:
- custom_animation: Main animation loop and control
- update_positions: Physics and state updates for each frame
- update_plot: Visualization updates for each frame
- init_plot: Initialize the plot with all entities
- CheckProbability: Probabilistic event generation
- toggle_pause: Pause/resume handler

Author: Jorge
Date: 2024
"""

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

# Global state variables
check = False  # Flag to check for events periodically
paused = False  # Animation pause state

def toggle_pause(event):
    """Toggle animation pause state when pause button is clicked."""
    global paused
    paused = not paused

def CheckProbability(probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA,Event):
    """
    Probabilistically generate dynamic events during simulation.
    
    Checks various event probabilities and randomly triggers events like:
    - Task appearance/disappearance
    - Vehicle appearance/breakdown
    - Implement appearance/disappearance
    
    Args:
        probabilityTA, probabilityTD: Task appearance/disappearance probabilities
        probabilityVA, probabilityVD: Vehicle appearance/disappearance probabilities
        probabilityIA, probabilityID: Implement appearance/disappearance probabilities
        Event (list): Current event state [is_event, type, id]
    
    Returns:
        list: Updated event state
    """
    global check
    if check:
        check=False
        # Check each event type with its probability
        if random.random() < probabilityTA:
            Event=[True,"Task",1]  # Task appearance
        elif random.random() < probabilityTD:
            Event=[True,"Task",2]  # Task disappearance
        elif random.random() < probabilityVA:
            Event=[True,"Vehicle",1]  # New vehicle
        elif random.random() < probabilityVD:
            Event=[True,"Vehicle",2]  # Vehicle breakdown
        elif random.random() < probabilityIA:
            Event=[True,"Implement",1]  # New implement
        elif random.random() < probabilityID:
            Event=[True,"Implement",2]  # Implement disappearance
    
    return Event

def update_positions(Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, Z_vehicles,Distancia,probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA,totalDistancia,num_periods,Z_periodsD,vehicle_states,FinishedTasks,start_time):
    """
    Update vehicle positions and states for one animation frame.
    
    This function handles the core simulation logic:
    1. Moves vehicles toward their assigned implements
    2. Moves vehicle+implement pairs toward assigned tasks
    3. Moves idle vehicles back to depot
    4. Checks for task/implement/depot completion
    5. Triggers events when appropriate
    6. Tracks distances and timing
    
    Movement phases for each vehicle:
    - Phase 1: Vehicle to Implement (orange arrow)
    - Phase 2: Vehicle+Implement to Task (green arrow)
    - Phase 3: Vehicle to Depot (red arrow)
    
    Args:
        Vehicles, Implements, Tasks: Entity position matrices
        Asignments: Task assignments from optimization
        step_fraction: Current animation step
        Vl: Velocity for each vehicle
        reached_implements, reached_tasks: Boolean arrays tracking progress
        Z_vehicles: Vehicles assigned to depot
        Distancia, totalDistancia: Distance tracking arrays
        probability*: Event generation probabilities
        num_periods: Number of planning periods
        Z_periodsD: Depot assignment periods
        vehicle_states: Current period for each vehicle
        FinishedTasks: Number of completed tasks
        start_time: Simulation start time
    
    Returns:
        tuple: (Event, updated_Vehicles, updated_Implements, reached_info, 
                depot_reached_info, New_task, Distancia, totalDistancia, vehicle_states)
    """
    Event = [False, "", 0]
    Imp=False
    Depot=False
    XActual=Vehicles[:,0]
    YActual=Vehicles[:,1]
    New_task = []
    T=Vehicles[:,4]
    StoppedDepot=np.ones((len(Vehicles)))
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

                Implements[A_implements[i], 0] = Vehicles[A_vehicles[i], 0]
                Implements[A_implements[i], 1] = Vehicles[A_vehicles[i], 1]
                # Check if the vehicle has reached the task
                if np.linalg.norm([dx, dy]) < Vl[A_vehicles[i]]:
                    dif=np.linalg.norm([dx, dy])
                    reached_tasks[A_vehicles[i]] = True
                    Implements[A_implements[i], 0] = Tasks[A_tasks[i], 0]
                    Implements[A_implements[i], 1] = Tasks[A_tasks[i], 1]
                    end_time = time.time()
                    ttask= end_time - start_time
                    reached_info.append((A_implements[i], A_tasks[i], A_vehicles[i],int(vehicle_states[A_vehicles[i]]),ttask)) 
                    FinishedTasks+=1
                    if num_periods<=1:
                        Event = [True, "Simulation", 1]
                    else:
                        if vehicle_states[A_vehicles[i]]==num_periods-1: #choose when stop the simulation
                            Event = [True, "Simulation", 1]
                        elif (len(A_tasks)-FinishedTasks)==0:
                            Event = [True, "Simulation", 1]
                        else:
                            vehicle_states[A_vehicles[i]] = vehicle_states[A_vehicles[i]]+1
                            reached_implements[A_vehicles[i]] = False
                            reached_tasks[A_vehicles[i]] = False
            
            Vehicles[A_vehicles[i], 0] += Vl[A_vehicles[i]] * math.cos(alpha)
            Vehicles[A_vehicles[i], 1] += Vl[A_vehicles[i]] * math.sin(alpha) 
            Distancia[A_vehicles[i]] += Vl[A_vehicles[i]] 
            totalDistancia[A_vehicles[i]] += Vl[A_vehicles[i]]       
        else:
            # Move vehicle back to depot
            indiceZ = next((i for i in range(len(Z_periodsD)) if Z_periodsD[i] == vehicle_states[v] and Z_vehicles[i] == v), None)
            i=indiceZ
            dx = 1 - Vehicles[Z_vehicles[i], 0]
            dy = 1 - Vehicles[Z_vehicles[i], 1]
            alpha = math.atan2(dy, dx)
            
            
            StTask=Tasks[:,4]
            K=[k for k, State in enumerate(StTask) if State == 0]

            # Check if the vehicle has reached the depot
            if np.linalg.norm([dx, dy]) < Vl[Z_vehicles[i]]:
                dif=np.linalg.norm([dx, dy])
                Vehicles[Z_vehicles[i], 0] = 1
                Vehicles[Z_vehicles[i], 1] = 1
                if (T[Z_vehicles[i]]<10):
                    if num_periods<=1:
                        depot_reached_info.append((Z_vehicles[i],int(vehicle_states[Z_vehicles[i]])))
                        Event = [True, "Simulation", 2]
                    else:
                        if vehicle_states[Z_vehicles[i]]==num_periods-1:
                            depot_reached_info.append((Z_vehicles[i],int(vehicle_states[Z_vehicles[i]])))
                            Event = [True, "Simulation", 2]
                        else:
                            vehicle_states[Z_vehicles[i]] += 1
                else:
                    StoppedDepot[Z_vehicles[i]]=0
            else:            
                Vehicles[Z_vehicles[i], 0] += Vl[Z_vehicles[i]] * math.cos(alpha)
                Vehicles[Z_vehicles[i], 1] += Vl[Z_vehicles[i]] * math.sin(alpha)
                distance_moved = Vl[Z_vehicles[i]]
                Distancia[Z_vehicles[i]]+= distance_moved
                totalDistancia[Z_vehicles[i]]+= distance_moved
                            
    Event=CheckProbability(probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA,Event)


    if Event[1]=="Simulacion" or Imp:
        for v in range(num_vehicles):
            if StoppedDepot[v]==1:
                dx=XActual[v]-Vehicles[v,0]
                dy=YActual[v]-Vehicles[v,1]
                alpha=math.atan2(dy,dx)
                excess = Vl[v] - dif 
                Vehicles[v,1] -= excess * math.sin(alpha)
                Vehicles[v,0] -= excess * math.cos(alpha)
                Distancia[v]-= excess
                totalDistancia[v] -= excess
        Imp=False

            
    return Event, Vehicles, Implements, reached_info,depot_reached_info, New_task,Distancia,totalDistancia,vehicle_states

def init_plot(ax, Implements, Tasks, Vehicles):
    """
    Initialize the visualization plot with all entities.
    
    Displays:
    - Implements: Black triangles
    - Tasks: Blue squares (available) or red squares (completed)
      Size proportional to task area
    - Vehicles: Red hexagons with labels
    - Depot: Green square at origin (0,0)
    
    Args:
        ax: Matplotlib axes object
        Implements, Tasks, Vehicles: Entity position matrices
    """
    ax.clear()
    
    # Plot implements as black triangles
    ax.scatter(Implements[:, 0], Implements[:, 1], marker="^", s=10**2, c="black", label="Implements")

    # Plot tasks with size proportional to area, color by state
    for i in range(len(Tasks)):
        if Tasks[i, -1] == 0:  # Available task
            ax.scatter(Tasks[i, 0], Tasks[i, 1], c="blue", marker="s", alpha=0.3, s=Tasks[i, 2] * 20)
            ax.scatter(Tasks[i, 0], Tasks[i, 1], c="blue", marker="s", alpha=1, s=20, label="Task Available" if i == 0 else "")
        else:  # Completed task
            ax.scatter(Tasks[i, 0], Tasks[i, 1], c="red", marker="s", alpha=0.3, s=Tasks[i, 2] * 20 )
            ax.scatter(Tasks[i, 0], Tasks[i, 1], c="red", marker="s", alpha=1, s=20, label="Task Not Available" if i == 1 else "")

    # Plot depot at origin
    ax.scatter(0, 0, marker="s", s=10**2, c="green", label="Depot", alpha=0.4)
    
    # Plot vehicles as red hexagons with labels
    ax.scatter(Vehicles[:, 0], Vehicles[:, 1], marker="H", s=10**2, c="red", label="Vehicles")
    for i in range(len(Vehicles)):
        ax.text(Vehicles[i, 0], Vehicles[i, 1], f'V{i}', fontsize=12, ha='right')

    ax.set_title("Allocation Problem")
    ax.legend(loc='upper right')
    ax.set_xlim(-1, 100)
    ax.set_ylim(-1, 100)


def update_plot(ax, Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, Z_vehicles, Distancia, probabilityTA, probabilityTD, probabilityVA, probabilityVD, probabilityID, probabilityIA,totalDistancia,num_periods,Z_periodsD,vehicle_states,FinishedTasks,start_time):
    """
    Update the visualization for one animation frame.
    
    This function:
    1. Calls update_positions to get new positions
    2. Re-initializes the plot with updated positions
    3. Draws arrows showing current vehicle objectives
    
    Arrow colors indicate vehicle state:
    - Orange: Moving toward implement
    - Green: Moving toward task (with implement)
    - Red: Returning to depot
    
    Args:
        ax: Matplotlib axes object
        (other args same as update_positions)
    
    Returns:
        tuple: (Event, updated_vehicles, updated_implements, reached_info,
                depot_reached_info, New_task, totalDistancia, vehicle_states)
    """
    ax.clear()
    
    Event, updated_vehicles, updated_implements, reached_info,depot_reached_info, New_task, Distancia,totalDistancia,vehicle_states = update_positions(Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, Z_vehicles, Distancia, probabilityTA, probabilityTD, probabilityVA, probabilityVD, probabilityID, probabilityIA,totalDistancia,num_periods,Z_periodsD,vehicle_states,FinishedTasks,start_time)

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
    """
    Main animation controller for the D-MRTAI simulation.
    
    Creates an interactive matplotlib animation showing vehicles executing their
    assigned tasks in real-time. Includes a pause button and handles events
    that may trigger re-optimization.
    
    The animation runs until:
    - All tasks are completed
    - An event requiring re-optimization occurs
    - User closes the window
    
    Args:
        Implements, Tasks, Vehicles: Initial entity positions
        Asignments: Task assignments from optimization (x variables)
        ZAsignments: Depot assignments from optimization (z variables)
        probability*: Event generation probabilities
        jota: Animation iteration offset
        totalDistancia: Cumulative distances per vehicle
        num_periods: Number of planning periods
        num_steps: Animation steps per iteration (default: 100)
    
    Returns:
        tuple: (Event, Vehicles, Implements, Tasks, reached_info_all, 
                depot_reached_info_all, execution_time, Distancia, totalDistancia)
            - Event: Final event that stopped simulation
            - Updated entity positions
            - reached_info_all: List of completed task assignments with timing
            - depot_reached_info_all: List of depot visits
            - execution_time: Total simulation time in seconds
            - Distance tracking arrays
    """
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
        FinishedTasks=len(reached_info_all)
        # Actualiza la gráfica y obtén los eventos
        Event, updated_vehicles, updated_implements, reached_info, depot_reached_info, New_task, totalDistancia, vehicle_states = update_plot(
            ax, Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks,
            Z_vehicles, Distancia, probabilityTA, probabilityTD, probabilityVA, probabilityVD, probabilityID,
            probabilityIA, totalDistancia, num_periods, Z_periodsD, vehicle_states,FinishedTasks,start_time
        )
        # Almacenar la información de los vehículos que han llegado
        reached_info_all.extend(reached_info)
        depot_reached_info_all.extend(depot_reached_info)

        # Verificar si hay eventos para detener la simulación
        if Event[0]:
            print (
                    "***************************************************************************************************************\n"
                    f"                   EVENT TRIGGERED - SIMULATION STOPPED\n"
                    "***************************************************************************************************************"
                )
            end_time = time.time()
            execution_time = end_time - start_time
            plt.close(fig)
            return False,execution_time  # Indica que la animación debe detenerse
        
        return True,None

    def run_animation(jota,totalDistancia,vehicle_states):
        global check
        i = 0
        stop=True
        while stop:
            step_fraction = ((i + 1) / num_steps) + jota
            stop,execution_time=update_frame(step_fraction,totalDistancia,vehicle_states)
            plt.pause(0.001)
            i += 1
            if i % 5 == 0:
                check=True
            if i == num_steps:
                jota += 1
                i = 0

        return execution_time

    ax_pause = plt.axes([0.45, 0.01, 0.1, 0.05])
    btn_pause = Button(ax_pause, "Pausa")
    btn_pause.on_clicked(toggle_pause)
    
    execution_time=run_animation(jota,totalDistancia,vehicle_states)

    return Event, Vehicles, Implements, Tasks, reached_info_all, depot_reached_info_all, execution_time, Distancia, totalDistancia

