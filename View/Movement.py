import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random
import math

def update_positions(Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements,reached_tasks):
    num_vehicles = len(Vehicles)

    A_implements = []
    A_tasks = []
    A_vehicles = []

    for key, value in Asignments.items():
        _, i, j, k = key.split('_')
        A_implements.append(int(i))
        A_tasks.append(int(j))
        A_vehicles.append(int(k))

    for i in range(num_vehicles):
        if not reached_implements[A_vehicles[i]]:
            # Move vehicles towards their respective implements
            dx = Implements[A_implements[i], 0] - Vehicles[A_vehicles[i], 0]
            dy = Implements[A_implements[i], 1] - Vehicles[A_vehicles[i], 1]
            alpha = math.atan2(dy, dx)

            Vehicles[A_vehicles[i], 0] += Vl[i] * math.cos(alpha)
            Vehicles[A_vehicles[i], 1] += Vl[i] * math.sin(alpha)
            
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

            # Check if the vehicle has reached the task
            if np.linalg.norm([dx, dy]) < Vl[i]:
                reached_tasks[A_vehicles[i]] = True
                Vehicles[A_vehicles[i], 0] = Tasks[A_tasks[i], 0]
                Vehicles[A_vehicles[i], 1] = Tasks[A_tasks[i], 1]
                Implements[A_implements[i], 0] = Tasks[A_tasks[i], 0]
                Implements[A_implements[i], 1] = Tasks[A_tasks[i], 1]
        else:
            Vehicles[A_vehicles[i], 0] = Tasks[A_tasks[i], 0]
            Vehicles[A_vehicles[i], 1] = Tasks[A_tasks[i], 1]
            Implements[A_implements[i], 0] = Vehicles[A_vehicles[i], 0]
            Implements[A_implements[i], 1] = Vehicles[A_vehicles[i], 1]

    return Vehicles, Implements

def init_plot(ax, Implements, Tasks, Vehicles):
    ax.clear()
    ax.scatter(Implements[:, 0], Implements[:, 1], marker="^", s=10**2, c="black", label="Implements")
    ax.scatter(Tasks[:, 0], Tasks[:, 1], c="blue", marker="s", alpha=0.3, s=Tasks[:, 2] * 20)
    ax.scatter(Tasks[:, 0], Tasks[:, 1], c="blue", marker="s", label="Tasks", alpha=1)
    ax.scatter(0, 0, marker="s", s=10**2, c="green", label="Depot", alpha=0.4)
    ax.scatter(Vehicles[:, 0], Vehicles[:, 1], marker="H", s=10**2, c="red", label="Vehicles")

    ax.set_title("Allocation Problem")
    ax.legend(loc='upper right')
    ax.set_xlim(-1, 100)
    ax.set_ylim(-1, 100)

def update_plot(ax, Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements,reached_tasks):
    ax.clear()
    updated_vehicles, updated_implements = update_positions(Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements,reached_tasks)
    init_plot(ax, updated_implements, Tasks, updated_vehicles)

    num_vehicles = len(Vehicles)

    A_implements = []
    A_tasks = []
    A_vehicles = []

    for key, value in Asignments.items():
        _, i, j, k = key.split('_')
        A_implements.append(int(i))
        A_tasks.append(int(j))
        A_vehicles.append(int(k))

    for i in range(num_vehicles):
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

    ax.set_title(f"Vehicle Movements - Step Fraction {step_fraction:.2f}")

def animate_allocation(Implements, Tasks, Vehicles, Asignments, num_steps=100):
    fig, ax = plt.subplots(figsize=(100, 6))
    reached_implements = np.full(len(Vehicles), False)
    reached_tasks = np.full(len(Tasks), False)
    Vl = [2] * len(Vehicles)
    def animate(i):
        step_fraction = i / num_steps
        update_plot(ax, Vehicles, Implements, Tasks, Asignments, step_fraction, Vl, reached_implements,reached_tasks)

    ani = animation.FuncAnimation(fig, animate, frames=num_steps, interval=100)
    plt.show()

# Example usage:
