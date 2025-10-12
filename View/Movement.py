"""
Movement.py - Animated Simulation and Visualization for D-MRTAI

This module provides real-time animated visualization of vehicle movements executing
the optimized task assignments. It simulates vehicle trajectories, tracks progress,
and can trigger dynamic events during execution.

Key Features:
- Real-time matplotlib animation of vehicle movements
- Three-phase movement: vehicle→implement→task
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
import math
import random
from Tools import Defactorise as tl
import time
import matplotlib
from Events import EventLogger as EVlogger
from Events import Events as EV
import time
matplotlib.use('GTK3Agg')
<<<<<<< Updated upstream

def update_positions(Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, Z_vehicles,Distancia,probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA):
=======

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
    - Phase 1: Vehicle → Implement (orange arrow)
    - Phase 2: Vehicle+Implement → Task (green arrow)
    - Phase 3: Vehicle → Depot (red arrow)
    
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
>>>>>>> Stashed changes
    Event = [False, "", 0]
    New_task = []
    A_implements, A_tasks, A_vehicles = tl.XAsignmentsDefactorise(Asignments)
    num_vehicles = len(A_vehicles)
    num_tasks = len(Tasks)
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

<<<<<<< Updated upstream
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
                Event = [True, "Simulation", 1]
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
            if num_vehicles<num_tasks:
                Event = [True, "Simulation", 2]

    #Check if a new task appear
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
    
    

    return Event, Vehicles, Implements, reached_info, New_task,Distancia

def init_plot(ax, Implements, Tasks, Vehicles):
    ax.clear()
    ax.scatter(Implements[:, 0], Implements[:, 1], marker="^", s=10**2, c="black", label="Implements")
    ax.scatter(Tasks[:, 0], Tasks[:, 1], c="blue", marker="s", alpha=0.3, s=Tasks[:, 2] * 20)
    ax.scatter(Tasks[:, 0], Tasks[:, 1], c="blue", marker="s", label="Tasks", alpha=1)
=======
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
>>>>>>> Stashed changes
    ax.scatter(0, 0, marker="s", s=10**2, c="green", label="Depot", alpha=0.4)
    
    # Plot vehicles as red hexagons with labels
    ax.scatter(Vehicles[:, 0], Vehicles[:, 1], marker="H", s=10**2, c="red", label="Vehicles")
<<<<<<< Updated upstream

    # Add vehicle labels
=======
>>>>>>> Stashed changes
    for i in range(len(Vehicles)):
        ax.text(Vehicles[i, 0], Vehicles[i, 1], f'V{i}', fontsize=12, ha='right')

    ax.set_title("Allocation Problem")
    ax.legend(loc='upper right')
    ax.set_xlim(-1, 100)
    ax.set_ylim(-1, 100)

<<<<<<< Updated upstream
def update_plot(ax, Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, Z_vehicles,Distancia,probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA):
=======

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
>>>>>>> Stashed changes
    ax.clear()
    Event, updated_vehicles, updated_implements, reached_info,New_task,Distancia= update_positions(Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, Z_vehicles,Distancia,probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA)
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


<<<<<<< Updated upstream
    ax.set_title(f"Vehicle Movements - Step Fraction {step_fraction:.2f}")
    return Event, updated_vehicles, updated_implements, reached_info,New_task

def animate_allocation(Implements, Tasks, Vehicles, Asignments, ZAsignments,probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA,num_steps=100):
    start_time = time.time()  # Registrar el tiempo de inicio
=======
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
>>>>>>> Stashed changes
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
        Event, updated_vehicles, updated_implements, reached_info, New_task = update_plot(ax, Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, Z_vehicles,Distancia,probabilityTA,probabilityTD,probabilityVA,probabilityVD,probabilityID,probabilityIA)
        reached_info_all.extend(reached_info)  # Agregar la información de los vehículos que han llegado en este paso
        if Event[0]:
            print("***************************************************************************************************************")
            print("                                 EVENT TRIGERED-SIMULATION STOPPED         ")
            print("***************************************************************************************************************")
            event_occurred = True
            end_time = time.time()  # Registrar el tiempo de finalización
            execution_time = end_time - start_time  # Calcular el tiempo de ejecución
            ani.event_source.stop()
            time.sleep(0.75)
            plt.close(fig)

    ani = animation.FuncAnimation(fig, animate, frames=num_steps, interval=100)
    plt.show()

    return Event, Vehicles, Implements, Tasks, reached_info_all, execution_time, Distancia
