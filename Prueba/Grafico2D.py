import pandas as pd
import matplotlib.pyplot as plt

# Leer archivo CSV
df = pd.read_csv('Results.csv', sep=';')
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

# Crear subplots en 2D
fig, axs = plt.subplots(3, 3, figsize=(20, 15))
fig.suptitle("Métricas por Nº de Tareas (series por Nº de Períodos)", fontsize=20)

# Obtener valores únicos de periodos
periods = sorted(df['num_periods'].unique())

for idx, (metric, title) in enumerate(metrics.items()):
    row, col = divmod(idx, 3)
    ax = axs[row][col]

    for p in periods:
        subset = df[df['num_periods'] == p]
        avg_by_tasks = subset.groupby('num_tasks')[metric].mean()
        ax.plot(avg_by_tasks.index, avg_by_tasks.values, label=f'Periodos = {p}')

    ax.set_title(title, fontsize=12)
    ax.set_xlabel("Nº de Tareas")
    ax.set_ylabel(title)
    ax.legend()
    ax.grid(True)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()
