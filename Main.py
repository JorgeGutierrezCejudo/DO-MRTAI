import tkinter as tk
from tkinter import ttk
import os
import json
import Data
import DoMRTAI as dm

# Directorio y balance de costos y energía
CostBalance = [1, 0.01]
EnergyBalance = [1, 0.2]

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
        "dataset": dataset_entry.get(),
        "full": full_var.get(),
        "time_horizon": time.get(),
        "num_periods": periods.get()
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

    save_config()

    print("***************************************************************************************************************")
    print(f"Running DO-MRTAI algorithm for {num_implements} implements, {num_tasks} tasks and {num_vehicles} vehicles.")
    print("***************************************************************************************************************")
    print()

    os.chdir(dir)
    Implements, Tasks, Vehicles = Data.PositionData(num_implements, num_tasks, num_vehicles, set_data)
    os.chdir(dir)
    dm.init(Implements, Tasks, Vehicles, T, num_periods)

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

ttk.Label(root, text="Dataset:").grid(row=3, column=0, padx=10, pady=5)
dataset_entry = ttk.Entry(root)
dataset_entry.grid(row=3, column=1, padx=10, pady=5)
dataset_entry.insert(0, config.get("dataset", ""))

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

ttk.Button(root, text="Run Optimization", command=run_optimization).grid(row=8, column=0, columnspan=2, pady=10)

root.mainloop()
