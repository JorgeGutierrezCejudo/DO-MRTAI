import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import math

def update_positions(Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, A_implements, A_tasks, A_vehicles, A_period, periods, Z_vehicles, Z_periods, task_completed):
    num_vehicles = len(Vehicles)
    num_asignments = len(Asignments)
    
    for i in range(num_asignments):
        vehicle_idx = A_vehicles[i]
        current_period = periods[vehicle_idx]
        
        if current_period == A_period[i]:
            if not reached_implements[vehicle_idx]:
                # Move vehicles towards their respective implements
                dx = Implements[A_implements[i], 0] - Vehicles[vehicle_idx, 0]
                dy = Implements[A_implements[i], 1] - Vehicles[vehicle_idx, 1]
                alpha = math.atan2(dy, dx)

                Vehicles[vehicle_idx, 0] += Vl[vehicle_idx] * math.cos(alpha)
                Vehicles[vehicle_idx, 1] += Vl[vehicle_idx] * math.sin(alpha)
                
                # Check if the vehicle has reached the implement
                if np.linalg.norm([dx, dy]) < Vl[vehicle_idx]:
                    reached_implements[vehicle_idx] = True
                    Vehicles[vehicle_idx, 0] = Implements[A_implements[i], 0]
                    Vehicles[vehicle_idx, 1] = Implements[A_implements[i], 1]
            elif not reached_tasks[vehicle_idx]:
                # Move combined vehicle and implement towards their respective tasks
                dx = Tasks[A_tasks[i], 0] - Vehicles[vehicle_idx, 0]
                dy = Tasks[A_tasks[i], 1] - Vehicles[vehicle_idx, 1]
                alpha = math.atan2(dy, dx)

                Vehicles[vehicle_idx, 0] += Vl[vehicle_idx] * math.cos(alpha)
                Vehicles[vehicle_idx, 1] += Vl[vehicle_idx] * math.sin(alpha)
                Implements[A_implements[i], 0] = Vehicles[vehicle_idx, 0]
                Implements[A_implements[i], 1] = Vehicles[vehicle_idx, 1]

                # Check if the vehicle has reached the task
                if np.linalg.norm([dx, dy]) < Vl[vehicle_idx]:
                    reached_tasks[vehicle_idx] = True
                    task_completed[A_tasks[i]] = True  # Mark the task as completed
                    Vehicles[vehicle_idx, 0] = Tasks[A_tasks[i], 0]
                    Vehicles[vehicle_idx, 1] = Tasks[A_tasks[i], 1]
                    Implements[A_implements[i], 0] = Tasks[A_tasks[i], 0]
                    Implements[A_implements[i], 1] = Tasks[A_tasks[i], 1]
                    periods[vehicle_idx] += 1  # Move to next period for this vehicle
                    reached_implements[vehicle_idx] = False  # Reset for next period
                    reached_tasks[vehicle_idx] = False
            else:
                Vehicles[vehicle_idx, 0] = Tasks[A_tasks[i], 0]
                Vehicles[vehicle_idx, 1] = Tasks[A_tasks[i], 1]
                Implements[A_implements[i], 0] = Vehicles[vehicle_idx, 0]
                Implements[A_implements[i], 1] = Vehicles[vehicle_idx, 1]

        elif (vehicle_idx in Z_vehicles) and (Z_periods[Z_vehicles.index(vehicle_idx)] == periods[vehicle_idx]):
                # Move vehicle back to depot
                dx = 1 - Vehicles[vehicle_idx, 0]
                dy = 1 - Vehicles[vehicle_idx, 1]
                alpha = math.atan2(dy, dx)
                Vehicles[vehicle_idx, 0] += (Vl[vehicle_idx]/2) * math.cos(alpha)
                Vehicles[vehicle_idx, 1] += (Vl[vehicle_idx]/2) * math.sin(alpha)
                if np.linalg.norm([dx, dy]) < Vl[vehicle_idx]:
                    Vehicles[vehicle_idx, 0] = 1
                    Vehicles[vehicle_idx, 1] = 1
                    periods[vehicle_idx] += 1  # Move to next period for this vehicle
                    reached_implements[vehicle_idx] = False
                    reached_tasks[vehicle_idx] = False   

    return Vehicles, Implements

def init_plot(ax, Implements, Tasks, Vehicles, task_completed, vehicle_labels):
    ax.clear()
    ax.scatter(Implements[:, 0], Implements[:, 1], marker="^", s=10**2, c="black", label="Implements")
    
    # Separate tasks into completed and not completed
    completed_tasks = Tasks[task_completed]
    not_completed_tasks = Tasks[~task_completed]
    
    # Plot tasks
    ax.scatter(not_completed_tasks[:, 0], not_completed_tasks[:, 1], c="blue", marker="s", alpha=0.3, s=not_completed_tasks[:, 2] * 20)
    ax.scatter(completed_tasks[:, 0], completed_tasks[:, 1], c="green", marker="s", alpha=0.3, s=completed_tasks[:, 2] * 20)
    
    # Replot the completed tasks with higher alpha for visibility
    ax.scatter(not_completed_tasks[:, 0], not_completed_tasks[:, 1], c="blue", marker="s", label="Pending Tasks", alpha=1)
    ax.scatter(completed_tasks[:, 0], completed_tasks[:, 1], c="green", marker="s", label="Completed Tasks", alpha=1)
    
    ax.scatter(1, 1, marker="s", s=10**2, c="green", label="Depot", alpha=0.4)
    ax.scatter(Vehicles[:, 0], Vehicles[:, 1], marker="H", s=10**2, c="red", label="Vehicles")

    # Add vehicle labels
    for i in range(len(Vehicles)):
        ax.text(Vehicles[i,0],Vehicles[i,1], f'V{i}', fontsize=12, ha='right')

    ax.set_title("Allocation Problem")
    ax.legend(loc='upper right')
    ax.set_xlim(-1, 100)
    ax.set_ylim(-1, 100)

def update_plot(ax, Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, A_implements, A_tasks, A_vehicles, A_period, periods, Z_vehicles, Z_periods, task_completed, vehicle_labels):
    ax.clear()
    updated_vehicles, updated_implements = update_positions(Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, A_implements, A_tasks, A_vehicles, A_period, periods, Z_vehicles, Z_periods, task_completed)
    init_plot(ax, updated_implements, Tasks, updated_vehicles, task_completed, vehicle_labels)

    num_vehicles = len(Vehicles)
    num_asignments = len(Asignments)

    for i in range(num_asignments):
        current_period = periods[A_vehicles[i]]
        vehicle_idx = A_vehicles[i]
        if current_period == A_period[i]:
            imp_index = A_implements[i]
            task_index = A_tasks[i]
        
            if not reached_implements[A_vehicles[i]]:
                # Draw arrow from vehicle to implement
                ax.annotate("", xy=(Implements[imp_index, 0], Implements[imp_index, 1]), 
                            xytext=(Vehicles[A_vehicles[i], 0], Vehicles[A_vehicles[i], 1]),
                            arrowprops=dict(arrowstyle="->", lw=3, color="orange"))
            else:
                # Draw arrow from implement to task
                ax.annotate("", xy=(Tasks[task_index, 0], Tasks[task_index, 1]), 
                            xytext=(Implements[imp_index, 0], Implements[imp_index, 1]),
                            arrowprops=dict(arrowstyle="->", lw=3, color="green"))
        elif (vehicle_idx in Z_vehicles) and (Z_periods[Z_vehicles.index(vehicle_idx)] == periods[vehicle_idx]):
            # Draw arrow from vehicle to depot
            ax.annotate("", xy=(1, 1), 
                        xytext=(Vehicles[A_vehicles[i], 0], Vehicles[A_vehicles[i], 1]),
                        arrowprops=dict(arrowstyle="->", lw=3, color="red"))

    # Add vehicle labels
    for i in range(len(updated_vehicles)):
        ax.text(updated_vehicles[i,0],updated_vehicles[i,1], f'V{i}', fontsize=12, ha='right')

    ax.set_title("Vehicle Movements - Dynamic Periods")

def animate_allocation(Implements, Tasks, Vehicles, Asignments, Zasigments, num_steps=100):
    fig, ax = plt.subplots(figsize=(10, 6))
    reached_implements = np.full(len(Vehicles), False)
    reached_tasks = np.full(len(Vehicles), False)
    Vl = [2] * len(Vehicles)
    periods = np.zeros(len(Vehicles), dtype=int)
    A_implements = []
    A_tasks = []
    A_vehicles = []
    A_periods = []
    for key, value in Asignments.items():
        _, i, j, k, t = key.split('_')
        A_implements.append(int(i))
        A_tasks.append(int(j))
        A_vehicles.append(int(k))
        A_periods.append(int(t))

    Z_vehicles = []
    Z_periods = []

    for key, value in Zasigments.items():
        _, i, t = key.split('_')
        Z_vehicles.append(int(i))
        Z_periods.append(int(t))
    
    task_completed = np.full(len(Tasks), False)

    def animate(i):
        step_fraction = 1
        update_plot(ax, Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements, reached_tasks, A_implements, A_tasks, A_vehicles, A_periods, periods, Z_vehicles, Z_periods, task_completed, A_vehicles)

    ani = animation.FuncAnimation(fig, animate, frames=num_steps, interval=100)
    plt.show()
