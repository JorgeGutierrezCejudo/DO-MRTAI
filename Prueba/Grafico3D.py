import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Leer archivo CSV
df = pd.read_csv('Results-Log.csv', sep=';')
df.columns = df.columns.str.strip()

# Convertir columnas necesarias a numérico
columns_to_convert = [
    'num_tasks', 'num_periods',
    't', 'toptimization',
    'DesvTaskDone', 'DesvDistancia',
    'PenaltyCost', 'StaticCost', 'DistanciaTotal', 'Obj'
]

for col in columns_to_convert:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df.dropna(subset=columns_to_convert, inplace=True)

# Métricas a graficar
metrics = {
    't': 'Tiempo Total',
    'toptimization': 'Tiempo de Optimización',
    'DesvTaskDone': 'Desviación Tareas Hechas',
    'DesvDistancia': 'Desviación de Distancia',
    'PenaltyCost': 'Coste por Penalización',
    'StaticCost': 'Coste Estático',
    'DistanciaTotal': 'Distancia Total',
    'Obj': 'Función Objetivo'
}

# Crear subplots
fig = plt.figure(figsize=(22, 16))
fig.suptitle("Métricas en Superficies 3D", fontsize=20)

for idx, (metric, title) in enumerate(metrics.items(), 1):
    pivot = df.pivot_table(index='num_tasks', columns='num_periods', values=metric)
    X, Y = np.meshgrid(pivot.columns, pivot.index)
    Z = pivot.values

    ax = fig.add_subplot(3, 3, idx, projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='k')

    ax.set_title(title, fontsize=13)
    ax.set_xlabel('Nº Vehículos', fontsize=10)
    ax.set_ylabel('Nº Tareas', fontsize=10)
    ax.set_zlabel(title, fontsize=10)
    ax.tick_params(axis='both', labelsize=8)

    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)

# Ajuste de espaciado
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
