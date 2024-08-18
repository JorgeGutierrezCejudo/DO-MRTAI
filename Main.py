import tkinter as tk
from tkinter import ttk
import os
import json
import Data
import DoMRTAI as dm

# Directorio y balance de costos y energía
CostBalance = [1, 0.01]  # [Costo de estático, Costo de dinámico]
EnergyBalance = [1, 0.2] # [Energía de estático, Energía de dinámico]

# Archivo de configuración
config_file = "config.json"

def directory():
    desired_name = 'urjc-tv'
    initial_directory = '.'
    found_directory = None

    for dirpath, dirnames, filenames in os.walk(initial_directory):
        for dirname in dirnames:
            if desired_name in dirname:
                found_directory = os.path.join(dirpath, dirname)
                break
        if found_directory:
            break

    if found_directory:
        dir = found_directory
    else:
        dir = os.getcwd()
        print(f"No se encontró ningún directorio con la terminación '{desired_name}'.")

    return dir

def save_config():
    config = {
        "num_implements": num_implements_entry.get(),
        "num_tasks": num_tasks_entry.get(),
        "num_vehicles": num_vehicles_entry.get(),
        "seed": dataset_entry.get(),
        "full": full_var.get(),
        "time_horizon": time.get(),
        "num_periods": periods.get(),
        "probabilityTA": probabilityTA_entry.get(),
        "probabilityTD": probabilityTD_entry.get(),
        "probabilityVA": probabilityVA_entry.get(),
        "probabilityVD": probabilityVD_entry.get(),
        "probabilityIA": probabilityIA_entry.get(),
        "probabilityID": probabilityID_entry.get()
    }
    with open(config_file, 'w') as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

def run_optimization():
    
    num_implements = int(num_implements_entry.get())
    num_tasks = int(num_tasks_entry.get())
    num_vehicles = int(num_vehicles_entry.get())
    set_data = int(dataset_entry.get())
    full = full_var.get()
    T = int(time.get())
    num_periods = int(periods.get())
    probabilityTA = float(probabilityTA_entry.get())
    probabilityTD = float(probabilityTD_entry.get())
    probabilityVA = float(probabilityVA_entry.get())
    probabilityVD = float(probabilityVD_entry.get())
    probabilityIA = float(probabilityIA_entry.get())
    probabilityID = float(probabilityID_entry.get())

    save_config()

    print("***************************************************************************************************************")
    print(f"Running DO-MRTAI algorithm for {num_implements} implements, {num_tasks} tasks and {num_vehicles} vehicles.")
    print("***************************************************************************************************************")
    print()

    os.chdir(dir)
    Implements, Tasks, Vehicles = Data.PositionData(num_implements, num_tasks, num_vehicles, set_data)
    os.chdir(dir)
    
    # Pasa las nuevas probabilidades como parámetros adicionales si es necesario
    dm.init(Implements, Tasks, Vehicles, T, num_periods, 
            probabilityTA, probabilityTD, probabilityVA, probabilityVD, probabilityIA, probabilityID)  

dir = directory()
os.chdir(dir)
dir = os.getcwd()

root = tk.Tk()
root.title("Parameter Configuration")

config = load_config()

ttk.Label(root, text="Number of Implements:").grid(row=0, column=0, padx=10, pady=5)
num_implements_entry = ttk.Entry(root)
num_implements_entry.grid(row=0, column=1, padx=10, pady=5)
num_implements_entry.insert(0, config.get("num_implements", ""))

ttk.Label(root, text="Number of Tasks:").grid(row=1, column=0, padx=10, pady=5)
num_tasks_entry = ttk.Entry(root)
num_tasks_entry.grid(row=1, column=1, padx=10, pady=5)
num_tasks_entry.insert(0, config.get("num_tasks", ""))

ttk.Label(root, text="Number of Vehicles:").grid(row=2, column=0, padx=10, pady=5)
num_vehicles_entry = ttk.Entry(root)
num_vehicles_entry.grid(row=2, column=1, padx=10, pady=5)
num_vehicles_entry.insert(0, config.get("num_vehicles", ""))

ttk.Label(root, text="Seed:").grid(row=3, column=0, padx=10, pady=5)
dataset_entry = ttk.Entry(root)
dataset_entry.grid(row=3, column=1, padx=10, pady=5)
dataset_entry.insert(0, config.get("seed", ""))

full_var = tk.BooleanVar()
full_checkbox = ttk.Checkbutton(root, text="Full", variable=full_var)
full_checkbox.grid(row=4, column=0, columnspan=2, pady=5)
full_var.set(config.get("full", False))

ttk.Label(root, text="Time Horizon").grid(row=5, column=0, padx=10, pady=5)
time = ttk.Entry(root)
time.grid(row=5, column=1, padx=10, pady=5)
time.insert(0, config.get("time_horizon", ""))

ttk.Label(root, text="Number of periods").grid(row=6, column=0, padx=10, pady=5)
periods = ttk.Entry(root)
periods.grid(row=6, column=1, padx=10, pady=5)
periods.insert(0, config.get("num_periods", ""))

# Añadir nuevos cuadros de entrada para las probabilidades de aparición y desaparición de tareas, vehículos e implementos
ttk.Label(root, text="Probability of Task Appearance (TA):").grid(row=7, column=0, padx=10, pady=5)
probabilityTA_entry = ttk.Entry(root)
probabilityTA_entry.grid(row=7, column=1, padx=10, pady=5)
probabilityTA_entry.insert(0, config.get("probabilityTA", ""))

ttk.Label(root, text="Probability of Task Disappearance (TD):").grid(row=8, column=0, padx=10, pady=5)
probabilityTD_entry = ttk.Entry(root)
probabilityTD_entry.grid(row=8, column=1, padx=10, pady=5)
probabilityTD_entry.insert(0, config.get("probabilityTD", ""))

ttk.Label(root, text="Probability of Vehicle Appearance (VA):").grid(row=9, column=0, padx=10, pady=5)
probabilityVA_entry = ttk.Entry(root)
probabilityVA_entry.grid(row=9, column=1, padx=10, pady=5)
probabilityVA_entry.insert(0, config.get("probabilityVA", ""))

ttk.Label(root, text="Probability of Vehicle Disappearance (VD):").grid(row=10, column=0, padx=10, pady=5)
probabilityVD_entry = ttk.Entry(root)
probabilityVD_entry.grid(row=10, column=1, padx=10, pady=5)
probabilityVD_entry.insert(0, config.get("probabilityVD", ""))

ttk.Label(root, text="Probability of Implement Appearance (IA):").grid(row=11, column=0, padx=10, pady=5)
probabilityIA_entry = ttk.Entry(root)
probabilityIA_entry.grid(row=11, column=1, padx=10, pady=5)
probabilityIA_entry.insert(0, config.get("probabilityIA", ""))

ttk.Label(root, text="Probability of Implement Disappearance (ID):").grid(row=12, column=0, padx=10, pady=5)
probabilityID_entry = ttk.Entry(root)
probabilityID_entry.grid(row=12, column=1, padx=10, pady=5)
probabilityID_entry.insert(0, config.get("probabilityID", ""))

ttk.Button(root, text="Run Optimization", command=run_optimization).grid(row=13, column=0, columnspan=2, pady=10)

root.mainloop()
