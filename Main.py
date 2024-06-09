import tkinter as tk
from tkinter import ttk
import os
import Data
import inspect
import pandas as pd

#dir="/Volumes/TOSHIBA EXT/Workspace/"
#dir="/home/jorgeurjc/WorkSpace/Optimization/"
CostBalance=[1,0.01]
EnergyBalance=[1,0.2]

def directory():
    
    desired_name = 'urjc-tv'
    initial_directory = '.'
    found_directory = None

    # Recorrer los directorios y subdirectorios
    for dirpath, dirnames, filenames in os.walk(initial_directory):
        for dirname in dirnames:
            if desired_name in dirname:
                found_directory = os.path.join(dirpath, dirname)
                break
            if found_directory:
                break

    if found_directory:
        dir=found_directory
    else:
        dir=os.getcwd()
        print(f"No se encontró ningún directorio con la terminación '{desired_name}'.")

    return dir
   



def get_model_inputs(model):
    try:
        signature = inspect.signature(model.Optimization)
        return list(signature.parameters.keys())
    except AttributeError:
        print("Error: Model does not have an Optimization function.")
        return []

def on_model_selected(*args):
    selected_model = model_var.get()
    if selected_model.startswith("Dynamic"):
        num_periods_entry.grid(row=11, column=1, padx=10, pady=5)
        full_checkbox.grid(row=4, column=0, columnspan=2, pady=5)
    else:
        num_periods_entry.grid_forget()
        full_checkbox.grid(row=4, column=0, columnspan=2, pady=5)

def run_optimization():
    selected_model = model_var.get()
    num_implements = int(num_implements_entry.get())
    num_tasks = int(num_tasks_entry.get())
    num_vehicles = int(num_vehicles_entry.get())
    set_data = int(dataset_entry.get())
    full = full_var.get()
    alpha = float(alpha_entry.get())
    beta = float(beta_entry.get())
    gamma = float(gamma_entry.get())
    GlobalResults = {}

    if selected_model in models:
        if selected_model.startswith("Dynamic"):
            num_periods = int(num_periods_entry.get())
            # print("Running optimization for", i, "tasks and", j, "vehicles.")
        else:
            num_periods = 1
        print("***************************************************************************************************************")  
        print("Running optimization(",selected_model,")for", num_implements, "implements,", num_tasks, "tasks and", num_vehicles, "vehicles.") 
        print("***************************************************************************************************************")
        print()
        os.chdir(dir)
        C, M, That, I, K, V, Mmax, Cmax,T_max = Data.CostData(num_implements, num_tasks, num_vehicles, set_data,num_periods,CostBalance)
        os.chdir(dir)
        IK, KI, IV, VI, KV, VK = Data.CompatibilityData(num_implements, num_tasks, num_vehicles, full)
        model = models[selected_model]
        model_inputs = get_model_inputs(model)
        os.chdir(dir)
        Specific = Data.SpecificData(model_inputs, set_data, num_vehicles,gamma,num_implements,num_tasks,num_periods,EnergyBalance)

        modelo=model.Optimization(C, M, That, I, K, V, Mmax, Cmax, IK, KI, IV, VI, KV, VK, alpha, beta, **Specific)       
        os.chdir(dir)
    else:
        print("Error: Selected model not found.")
    


dir=directory()
os.chdir(dir)
dir=os.getcwd()
root = tk.Tk()
root.title("Parameter Configuration")

ttk.Label(root, text="Number of Implements:").grid(row=0, column=0, padx=10, pady=5)
num_implements_entry = ttk.Entry(root)
num_implements_entry.grid(row=0, column=1, padx=10, pady=5)

ttk.Label(root, text="Number of Tasks:").grid(row=1, column=0, padx=10, pady=5)
num_tasks_entry = ttk.Entry(root)
num_tasks_entry.grid(row=1, column=1, padx=10, pady=5)

ttk.Label(root, text="Number of Vehicles:").grid(row=2, column=0, padx=10, pady=5)
num_vehicles_entry = ttk.Entry(root)
num_vehicles_entry.grid(row=2, column=1, padx=10, pady=5)

ttk.Label(root, text="Dataset:").grid(row=3, column=0, padx=10, pady=5)
dataset_entry = ttk.Entry(root)
dataset_entry.grid(row=3, column=1, padx=10, pady=5)

full_var = tk.BooleanVar()
full_checkbox = ttk.Checkbutton(root, text="Full", variable=full_var)
full_checkbox.grid(row=4, column=0, columnspan=2, pady=5)

ttk.Label(root, text="Alpha:").grid(row=5, column=0, padx=10, pady=5)
alpha_entry = ttk.Entry(root)
alpha_entry.grid(row=5, column=1, padx=10, pady=5)

ttk.Label(root, text="Beta:").grid(row=6, column=0, padx=10, pady=5)
beta_entry = ttk.Entry(root)
beta_entry.grid(row=6, column=1, padx=10, pady=5)

ttk.Label(root, text="Gamma:").grid(row=7, column=0, padx=10, pady=5)
gamma_entry = ttk.Entry(root)
gamma_entry.grid(row=7, column=1, padx=10, pady=5)

# Añadir entrada para el número de periodos
ttk.Label(root, text="Number of Periods:").grid(row=11, column=0, padx=10, pady=5)
num_periods_entry = ttk.Entry(root)

model_files = os.listdir("Models")
models = {}

for file in model_files:
    if file.endswith(".py") and file != "__init__.py":
        model_name = os.path.splitext(file)[0]
        model_module = __import__("Models." + model_name, fromlist=[model_name])
        models[model_name] = model_module

ttk.Label(root, text="Select Optimization Model:").grid(row=8, column=0, padx=10, pady=5)
model_var = tk.StringVar()
model_dropdown = ttk.Combobox(root, textvariable=model_var, values=list(models.keys()))
model_dropdown.grid(row=8, column=1, padx=10, pady=5)
model_dropdown.set(list(models.keys())[0])

# Asignar el evento para cuando se seleccione un modelo
model_var.trace("w", on_model_selected)

ttk.Button(root, text="Run Optimization", command=run_optimization).grid(row=12, column=0, columnspan=2, pady=10)

root.mainloop()
