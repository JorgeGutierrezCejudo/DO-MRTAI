"""
Main.py - Multi-Robot Task Assignment with Implements (D-MRTAI)

This is the main entry point for the D-MRTAI optimization system. It provides a graphical user interface (GUI)
for configuring and running experiments related to multi-robot task allocation problems.

Main Features:
- Interactive GUI for parameter configuration
- Support for batch experiments from JSON configuration files
- Real-time visualization of optimization results
- CSV export of experimental results
- Integration with optimization algorithms and visualization tools

Author: Jorge
Date: 2024
"""

import tkinter as tk
from tkinter import ttk
import os
import json
import Data
import DoMRTAI as dm

# Cost and Energy Balance Configuration
# These weights determine the relative importance of static vs dynamic costs
CostBalance = [1, 0.01]    # [Static cost weight, Dynamic cost weight]
EnergyBalance = [1, 0.2]   # [Static energy weight, Dynamic energy weight]

<<<<<<< Updated upstream
# Archivo de configuración
config_file = "config.json"
=======
# Configuration file path
default_config_file = "ConfigFile/config.json"
dir=os.getcwd()

# Create results directory if it doesn't exist
results_dir = "Results"
os.makedirs(results_dir, exist_ok=True)

# CSV file for storing experiment results
csv_file = os.path.join(results_dir, "Results.csv")

# CSV Headers: Define all columns for experiment results tracking
# Includes problem parameters, probabilities, timing metrics, costs, and performance indicators
csv_headers = [
    "num_implements", "num_tasks", "num_vehicles", "seed", "full", 
    "time_horizon", "num_periods", "probabilityTA", "probabilityTD",
    "probabilityVA", "probabilityVD", "probabilityIA", "probabilityID",
    "t", "toptimization", "Obj","PenaltyCost","StaticCost", "DistanciaTotal","Distancia_list","DesvDistancia","TaskDone_list","DesvTaskDone",
    "TotalTasksDone", "TasksCompleted"
]

# Initialize CSV file with headers if it doesn't exist
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline='') as f:
        writer = csv.writer(f,delimiter=";")
        writer.writerow(csv_headers)

def save_results_to_csv(experiment, t,toptimization,Obj,DoneAsignationCost,StaticCostTask,Distancia_list,InfoTaskDone):
    """
    Save experiment results to CSV file.
    
    Args:
        experiment (dict): Dictionary containing experiment parameters
        t (float): Total elapsed time of the simulation
        toptimization (float): Time spent on optimization
        Obj (float): Objective function value
        DoneAsignationCost (float): Cost of completed task assignments
        StaticCostTask (float): Static cost for tasks
        Distancia_list (list): List of distances traveled by each vehicle
        InfoTaskDone (list): Information about completed tasks per robot
    """
    Distancia_list = [item[1] for item in Distancia_list]
    DistanciaTotal= sum(Distancia_list)
    DesvDistancia=max(Distancia_list) - min(Distancia_list)
    InfoTaskDone = [item[1] for item in InfoTaskDone]
    DesvTaskDone= max(InfoTaskDone) - min(InfoTaskDone)
    TotalTasksDone = sum(InfoTaskDone)
    TasksCompleted = TotalTasksDone == int(experiment["num_tasks"])
    
    with open(csv_file, "a", newline='') as f:
        writer = csv.writer(f,delimiter=";")
        writer.writerow([
            experiment["num_implements"], experiment["num_tasks"], experiment["num_vehicles"], 
            experiment["seed"], experiment["full"], experiment["time_horizon"], 
            experiment["num_periods"], experiment["probabilityTA"], experiment["probabilityTD"],
            experiment["probabilityVA"], experiment["probabilityVD"], experiment["probabilityIA"], 
            experiment["probabilityID"], t, toptimization, Obj,DoneAsignationCost,StaticCostTask,DistanciaTotal,Distancia_list,DesvDistancia,InfoTaskDone,DesvTaskDone,
            TotalTasksDone, TasksCompleted
        ])

>>>>>>> Stashed changes

def directory():
    """
    Search for a specific directory within the project structure.
    
    This function looks for a directory containing 'urjc-tv' in its name.
    If found, it returns that directory path; otherwise, it returns the current working directory.
    
    Returns:
        str: Path to the found directory or current working directory
    """
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

<<<<<<< Updated upstream
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
=======
def run_experiment(experiment):
    """
    Execute a single optimization experiment with the given parameters.
    
    This function:
    1. Loads position data for implements, tasks, and vehicles
    2. Runs the D-MRTAI optimization algorithm
    3. Saves the results to a CSV file
    
    Args:
        experiment (dict): Dictionary containing all experiment parameters:
            - num_implements: Number of implements
            - num_tasks: Number of tasks
            - num_vehicles: Number of vehicles
            - seed: Random seed for reproducibility
            - full: Boolean indicating full compatibility matrices
            - time_horizon: Maximum simulation time
            - num_periods: Number of time periods
            - probabilityTA, probabilityTD: Task appearance/disappearance probabilities
            - probabilityVA, probabilityVD: Vehicle appearance/disappearance probabilities
            - probabilityIA, probabilityID: Implement appearance/disappearance probabilities
    """
    print(f"Running experiment: {experiment}")

    num_implements = int(experiment["num_implements"])
    num_tasks = int(experiment["num_tasks"])
    num_vehicles = int(experiment["num_vehicles"])
    seed = int(experiment["seed"])
    full = bool(experiment["full"])
    T = int(experiment["time_horizon"])
    num_periods = int(experiment["num_periods"])
    probabilityTA = float(experiment["probabilityTA"])
    probabilityTD = float(experiment["probabilityTD"])
    probabilityVA = float(experiment["probabilityVA"])
    probabilityVD = float(experiment["probabilityVD"])
    probabilityIA = float(experiment["probabilityIA"])
    probabilityID = float(experiment["probabilityID"])

    os.chdir(dir)
    Implements, Tasks, Vehicles = Data.PositionData(num_implements, num_tasks, num_vehicles, seed)
    os.chdir(dir)
    t,toptimization,Obj,DoneAsignationCost,StaticCostTask,Distancia_list,RobotPerformanceList = dm.init(
        Implements, Tasks, Vehicles, T, num_periods,
        probabilityTA, probabilityTD, probabilityVA, probabilityVD, probabilityIA, probabilityID, full, seed
    )

    save_results_to_csv(experiment, t,toptimization,Obj,DoneAsignationCost,StaticCostTask,Distancia_list,RobotPerformanceList)
    print("Experiment completed and results saved.")


def run_experiment_from_file(config_file):
    """
    Execute multiple experiments from a JSON configuration file.
    
    This function loads a batch of experiments from a JSON file and runs them sequentially,
    saving all results to a single CSV file. It also launches a visualization window to
    display real-time results.
    
    Args:
        config_file (str): Path to the JSON file containing experiment configurations
    """
    with open(config_file, 'r') as f:
        experiments = json.load(f)

    # Launch visualization window in a separate process
    visualization_process = subprocess.Popen(["python3.8", "View/Result.py"])

    # Execute each experiment sequentially
    for experiment in experiments:
        run_experiment(experiment)


def manual_entry():
    """
    Close the initial mode selection window and open the manual configuration window.
    """
    root.destroy()
    run_manual_configuration()


def load_file():
    """
    Open a file dialog to select a JSON configuration file and run experiments from it.
    """
    file_path = filedialog.askopenfilename(title="Select JSON Configuration File", filetypes=[("JSON Files", "*.json")])
    if file_path:
        run_experiment_from_file(file_path)


def run_manual_configuration():
    """
    Create and display the manual parameter configuration window.
    
    This function builds a comprehensive GUI that allows users to:
    - Input all experiment parameters manually
    - Load previously saved configurations
    - Save current configuration for future use
    - Run a single optimization experiment
    
    The GUI includes:
    - Input fields for all numerical parameters
    - Checkboxes for boolean options
    - University logos for branding
    - A run button to execute the optimization
    """
    dir = directory()
>>>>>>> Stashed changes
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
