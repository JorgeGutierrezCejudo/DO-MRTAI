import copy as copy
from pyscipopt import Model as Modelo
import numpy as np
import pandas as pd
import os

estado_vehiculos = [1, 1, 0, 0, 0]  # Esta sería la lista de estados de los vehículos
vehiculos_filtrados = [v for v, estado in enumerate(estado_vehiculos) if estado == 1]

# Filtrar implementos y tareas de manera similar si tienes un estado asociado a ellos
# Suponiendo que también tienes una lista `estado_implements` y `estado_tareas`
estado_implements = [1, 0, 0, 0, 0]  # Esta es solo un ejemplo
estado_tareas = [1, 1, 0, 0]         # Esta es solo un ejemplo

implementos_filtrados = [i for i, estado in enumerate(estado_implements) if estado == 1]
tareas_filtradas = [k for k, estado in enumerate(estado_tareas) if estado == 1]

I = implementos_filtrados
K = tareas_filtradas
V = vehiculos_filtrados
num_implements = len(estado_implements)
num_tasks = len(estado_tareas)
num_vehicles = len(estado_vehiculos)

KI =[[i for i in range(num_tasks)] for _ in range(num_implements)]
IK=[[i for i in range(num_implements)] for _ in range(num_tasks)]
IV=[[i for i in range(num_implements)] for _ in range(num_vehicles)]
VI=[[i for i in range(num_vehicles)] for _ in range(num_implements)]
KV=[[i for i in range(num_tasks)] for _ in range(num_vehicles)]
VK=[[i for i in range(num_vehicles)] for _ in range(num_tasks)]

print(VK)

# KI: Lista de implementos con las tareas compatibles
KI = [[k for k in K] for i in I]

# IK: Lista de tareas con los implementos compatibles
IK = [[i for i in I] for k in K]

# IV: Lista de implementos con los vehículos compatibles
IV = [[v for v in V] for i in I]

# VI: Lista de vehículos con los implementos compatibles
VI = [[i for i in I] for v in V]

# KV: Lista de tareas con los vehículos compatibles
KV = [[v for v in V] for k in K]

# VK: Lista de vehículos con las tareas compatibles
VK = [[k for k in K] for v in V]

print(VK)