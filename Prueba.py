import numpy as np
import matplotlib.pyplot as plt
from math import sqrt
import os

def TimeExtendCalculation(num_periods, num_implements, num_tasks, num_vehicles, C, Tasks, Implements, Vehicles, Csta):
    x_task = Tasks[:, 0]  # Coordenadas X de las tareas
    y_task = Tasks[:, 1]  # Coordenadas Y de las tareas
    Ct=np.zeros((num_periods,num_implements,num_tasks,num_vehicles))
    Ct[0,:,:,:]=C
    positions_over_time = np.zeros((num_periods, num_vehicles, 2))  # Guardar posiciones de vehículos

    # Para almacenar combinaciones seleccionadas
    max_combinations = int(num_tasks / 4) 
    selected_combinations_over_time = np.full((num_periods, num_vehicles, max_combinations, 2), -1, dtype=int)

    # Posiciones iniciales de los vehículos
    positions_over_time[0] = Vehicles[:, :2]

    for t in range(num_periods - 1):
        positions = np.zeros((num_vehicles, 2))

        for v in range(num_vehicles):
            # Tomar la matriz de costos para el vehículo v en el último periodo
            Cst_t = Ct[t, :, :, v]
            total_cost = np.sum(Cst_t)  # Suma total de costos para normalización

            if total_cost == 0:
                raise ValueError("Total cost is zero, probabilities cannot be computed.")

            # Calcular las probabilidades normalizadas para implementos y tareas
            probabilities = Cst_t / total_cost
            probabilities_flat = probabilities.flatten()

            # Seleccionar las combinaciones con menores costos
            num_selected_combinations = max(1, num_tasks // 2)
            selected_indices_flat = np.argsort(probabilities_flat)[:num_selected_combinations]

            # Obtener índices de implementos y tareas
            selected_indices = np.unravel_index(selected_indices_flat, Cst_t.shape)
            selected_implements, selected_tasks = selected_indices

            # Guardar combinaciones seleccionadas en el array
            selected_combinations = list(zip(selected_implements, selected_tasks))
            for idx, (implement, task) in enumerate(selected_combinations):
                if idx < max_combinations:
                    selected_combinations_over_time[t, v, idx] = [implement, task]

            # Obtener coordenadas de las tareas seleccionadas
            selected_x_task = x_task[selected_tasks]
            selected_y_task = y_task[selected_tasks]

            # Obtener probabilidades de las combinaciones seleccionadas
            selected_probabilities = probabilities[selected_implements, selected_tasks]

            # Normalizar probabilidades seleccionadas
            if selected_probabilities.sum() > 0:
                selected_probabilities /= selected_probabilities.sum()

            # Calcular la posición ponderada del vehículo
            positions[v, 0] = np.dot(selected_probabilities, selected_x_task)
            positions[v, 1] = np.dot(selected_probabilities, selected_y_task)


        positions_over_time[t + 1] = positions  # Guardar las posiciones para este período

        # Calcular nuevos costos dinámicos desde las posiciones probables
        Cstt = np.zeros((num_implements, num_tasks, num_vehicles))
        for i in range(num_implements):
            for k in range (num_tasks):
                for v in range(num_vehicles):
                    Xdiv=abs(xImplement[i]-xVehicle[v])
                    Ydiv=abs(yImplement[i]-yVehicle[v])
                    Distance1=sqrt(Xdiv**2+Ydiv**2)
                    Xdik=abs(xTask[k]-xImplement[i])
                    Ydik=abs(yTask[k]-yImplement[i])
                    Distance2=sqrt(Xdik**2+Ydik**2)
                    Cstt[i, k, v] = Distance1+Distance2
                    if Ct[t,i,k,v]==1000:
                        Cstt[i, k, v]=1000
        Cstt = 0.5 * Csta + 0.5 * Cstt
        # Actualizar matrices
        Ct[t+1,:,:,:]=Cstt
        for v in range(num_vehicles):
            for task in selected_tasks:
                Ct[t+1,:, task, v] = 1000  # Asignar un costo alto a las tareas seleccionadas
        
       

    return Ct, positions_over_time, selected_combinations_over_time


def plot_periodic_positions_with_combinations(positions_over_time, selected_combinations_over_time, num_periods, Tasks, Implements, Vehicles):
    cols = min(3, num_periods)  # Máximo de 3 columnas
    rows = -(-num_periods // cols)  # Calcular las filas necesarias

    fig, axes = plt.subplots(rows, cols, figsize=(6 * cols, 6 * rows), sharey=True, sharex=True)
    axes = axes.flatten()  # Asegurar que los ejes sean iterables uniformemente

    colors = [
        'red', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow', 'blue', 'brown',
        'pink', 'lime', 'teal', 'olive', 'navy', 'maroon', 'gold', 'silver', 'coral', 'aqua', 'darkgreen'
    ]

    for t in range(num_periods):
        ax = axes[t]

        # Dibujar las posiciones de las tareas
        ax.scatter(Tasks[:, 0], Tasks[:, 1], c='blue', marker='o', label='Tasks' if t == 0 else None)

        # Dibujar las posiciones de los implementos
        ax.scatter(Implements[:, 0], Implements[:, 1], c='black', marker='^', label='Implements' if t == 0 else None)

        # Dibujar las posiciones de los vehículos en este período
        for v in range(positions_over_time.shape[1]):
            ax.scatter(positions_over_time[t, v, 0], positions_over_time[t, v, 1],
                       color=colors[v % len(colors)], marker='x', s=50, label=f'Vehicle {v}' if t == 0 else None)

            # Resaltar combinaciones seleccionadas y dibujar flechas
            if t < len(selected_combinations_over_time):
                selected_combinations = selected_combinations_over_time[t, v]
                for implement_idx, task_idx in selected_combinations:
                    if task_idx != -1:  # Evitar flechas para valores por defecto
                        task_x, task_y = Tasks[task_idx, 0], Tasks[task_idx, 1]
                        ax.plot(
                            [positions_over_time[t, v, 0], task_x],
                            [positions_over_time[t, v, 1], task_y],
                            linestyle='dashed', color=colors[v % len(colors)], linewidth=1, alpha=0.7
                        )

        ax.set_title(f'Period {t + 1}')
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.grid(True)
        if t % cols == 0:  # Solo en la primera columna
            ax.set_ylabel("Y Coordinate")
        if t >= (rows - 1) * cols:  # Solo en la última fila
            ax.set_xlabel("X Coordinate")

    for ax in axes[num_periods:]:
        ax.axis('off')

    axes[0].legend(loc='upper right', bbox_to_anchor=(1.5, 1.5))
    plt.tight_layout()
    plt.show()

# Continúa con la configuración de parámetros y ejecución como en tu código original



# Configuración de parámetros para la prueba
num_periods = 6
num_implements = 10
num_tasks = 40
num_vehicles = 5
set_data = 4

# Generar coordenadas aleatorias para las tareas (X, Y)
os.chdir("Data/Positions/")
directory_path="Positions-("+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+")-"+str(set_data)

os.chdir(directory_path)
Implements = np.loadtxt('Implements.csv', delimiter=',',dtype=float).reshape(num_implements,4)
Tasks = np.loadtxt('Tasks.csv', delimiter=',', dtype=float).reshape(num_tasks,5)
Vehicles = np.loadtxt('Vehicles.csv', delimiter=',', dtype=float).reshape(num_vehicles,6)


xImplement = Implements[:, 0]
yImplement = Implements[:, 1]
xTask = Tasks[:, 0]
yTask = Tasks[:, 1]
xVehicle = Vehicles[:, 0]
yVehicle = Vehicles[:, 1]
Cd = np.zeros((num_implements, num_tasks, num_vehicles))

for i in range(num_implements):
    for k in range(num_tasks):
        for v in range(num_vehicles):
            Xdiv = abs(xImplement[i] - xVehicle[v])
            Ydiv = abs(yImplement[i] - yVehicle[v])
            Distance1 = sqrt(Xdiv**2 + Ydiv**2)
            Xdik = abs(xTask[k] - xImplement[i])
            Ydik = abs(yTask[k] - yImplement[i])
            Distance2 = sqrt(Xdik**2 + Ydik**2)
            Cd[i, k, v] = Distance1 + Distance2

CostBalance = [0.5, 0.5]
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
C = (CostBalance[0] * Cst + CostBalance[1] * Cd)

# Llamar a la función TimeExtendCalculation
Cstt, positions_over_time, selected_combinations_over_time = TimeExtendCalculation(
    num_periods, num_implements, num_tasks, num_vehicles, C, Tasks, Implements, Vehicles,Cst
)
# Llamar a la función de graficar
plot_periodic_positions_with_combinations(
    positions_over_time,
    selected_combinations_over_time,
    num_periods,
    Tasks,
    Implements,
    Vehicles
)

