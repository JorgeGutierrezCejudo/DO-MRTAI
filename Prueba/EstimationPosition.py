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

        # Calcular nuevos costos simbólicos para el siguiente período
        Cstt = np.zeros((num_implements, num_tasks, num_vehicles))
        for i in range(num_implements):
            for k in range (num_tasks):
                for v in range(num_vehicles):
                    # Calcular coste simbólico basado en:
                    # 1. Coste actual
                    # 2. Distancia actual a la tarea
                    # 3. Eficiencia del vehículo e implemento
                    current_distance = sqrt(
                        (x_task[k] - positions[v, 0])**2 + 
                        (y_task[k] - positions[v, 1])**2
                    )
                    
                    # Factor de eficiencia combinada
                    efficiency_factor = 1 / (Implements[i, 2] * Vehicles[v, 2])
                    
                    # Coste simbólico que refleja la incertidumbre
                    Cstt[i, k, v] = Ct[t, i, k, v] * (1 + current_distance/100) * efficiency_factor
        
        # Actualizar matrices con los nuevos costes
        Ct[t+1,:,:,:] = Cstt
        
        # Marcar las tareas completadas en el período anterior
        completed_tasks = set()
        for v in range(num_vehicles):
            for implement, task in selected_combinations_over_time[t, v]:
                if task != -1:  # Verificar que la tarea es válida
                    completed_tasks.add(task)
        
        # Actualizar costos para las tareas completadas
        for task in completed_tasks:
            # Marcar la tarea como completada con un costo muy alto pero no infinito
            # Esto permite que el modelo de optimización aún pueda considerarla si es absolutamente necesario
            Ct[t+1,:, task, :] = 1e6  # Un valor alto pero no infinito
        
        # Actualizar el estado de las tareas completadas
        for task in completed_tasks:
            Tasks[task, 2] = 0  # Marcar el área como 0 (tarea completada)
        
    print(Ct)

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
            # Calcular distancia al implemento
            Xdiv = abs(xImplement[i] - xVehicle[v])
            Ydiv = abs(yImplement[i] - yVehicle[v])
            Distance1 = sqrt(Xdiv**2 + Ydiv**2)
            
            # Calcular distancia de implemento a tarea
            Xdik = abs(xTask[k] - xImplement[i])
            Ydik = abs(yTask[k] - yImplement[i])
            Distance2 = sqrt(Xdik**2 + Ydik**2)
            
            # Calcular ángulos para estimar tiempo de giro
            angle1 = np.arctan2(Ydiv, Xdiv) if Xdiv != 0 else 0
            angle2 = np.arctan2(Ydik, Xdik) if Xdik != 0 else 0
            turn_angle = abs(angle2 - angle1)
            
            # Obtener parámetros del vehículo
            vehicle_speed = Vehicles[v, 3]  # Velocidad del vehículo
            vehicle_efficiency = Vehicles[v, 2]  # Eficiencia del vehículo
            
            # Calcular tiempo de desplazamiento
            travel_time1 = Distance1 / (vehicle_speed * vehicle_efficiency)
            travel_time2 = Distance2 / (vehicle_speed * vehicle_efficiency)
            
            # Calcular tiempo de giro (asumiendo velocidad de giro constante)
            turn_speed = 30  # grados por segundo
            turn_time = (turn_angle * 180 / np.pi) / turn_speed
            
            # Calcular consumo de energía/combustible
            energy_consumption = (Distance1 + Distance2) * (1 + turn_angle / (2 * np.pi))
            
            # Coste total considerando tiempo y energía
            Cd[i, k, v] = (travel_time1 + travel_time2 + turn_time) * (1 + energy_consumption/1000)

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

