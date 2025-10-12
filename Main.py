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
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import os
import json
import csv
from Data import Data 
from Algorithm import DoMRTAI as dm
import subprocess 

# Cost and Energy Balance Configuration
# These weights determine the relative importance of static vs dynamic costs
CostBalance = [1, 0.01]    # [Static cost weight, Dynamic cost weight]
EnergyBalance = [1, 0.2]   # [Static energy weight, Dynamic energy weight]

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
    """Close the initial mode selection window and open the manual configuration window."""
    root.destroy()
    run_manual_configuration()


def load_file():
    """Open a file dialog to select a JSON configuration file and run experiments from it."""
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
    os.chdir(dir)

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
        with open(default_config_file, 'w') as f:
            json.dump(config, f)

    def load_last_config():
        if os.path.exists(default_config_file):
            with open(default_config_file, 'r') as f:
                return json.load(f)
        return {}

    config = load_last_config()

    def run_optimization():
        save_config()
        visualization_process = subprocess.Popen(["python3.8", "View/Result.py"])
        experiment = {
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
        run_experiment(experiment)

        print("Manual optimization completed and results saved.")

    root = tk.Tk()
    root.title("Parameter Configuration")
    root.geometry("1100x1000")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel",
                    font=("Roboto", 12),
                    background="white",
                    foreground="black")
    style.configure("TButton",
                    font=("Roboto", 12, "bold"),
                    background="#b3b3b3",
                    foreground="black")
    style.map("TButton",
              background=[("active", "#999999")])

    root.configure(bg="white")

    header_frame = tk.Frame(root, bg="white")
    header_frame.pack(fill=tk.X, pady=10)

    logo1_image = Image.open("Logos/URJC-Logo.png")
    logo1_image = logo1_image.resize((192, 108), Image.ANTIALIAS)
    logo1_photo = ImageTk.PhotoImage(logo1_image)
    logo1_label = tk.Label(header_frame, image=logo1_photo, bg="white")
    logo1_label.image = logo1_photo
    logo1_label.pack(side=tk.LEFT, padx=10)

    title_label = tk.Label(header_frame, text="Parameter Configuration", font=("Roboto", 20, "bold"), bg="white", fg="black")
    title_label.pack(side=tk.LEFT, expand=True, padx=10)

    logo2_image = Image.open("Logos/Logo-Universita-Roma-Tor-Vergata.png")
    logo2_image = logo2_image.resize((192, 50), Image.ANTIALIAS)
    logo2_photo = ImageTk.PhotoImage(logo2_image)
    logo2_label = tk.Label(header_frame, image=logo2_photo, bg="white")
    logo2_label.image = logo2_photo
    logo2_label.pack(side=tk.RIGHT, padx=10)

    main_frame = tk.Frame(root, bg="white")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    fields = [
        ("Number of Implements:", "num_implements"),
        ("Number of Tasks:", "num_tasks"),
        ("Number of Vehicles:", "num_vehicles"),
        ("Seed:", "seed"),
        ("Time Horizon:", "time_horizon"),
        ("Number of Periods:", "num_periods"),
        ("Probability of Task Appearance (TA):", "probabilityTA"),
        ("Probability of Task Disappearance (TD):", "probabilityTD"),
        ("Probability of Vehicle Appearance (VA):", "probabilityVA"),
        ("Probability of Vehicle Disappearance (VD):", "probabilityVD"),
        ("Probability of Implement Appearance (IA):", "probabilityIA"),
        ("Probability of Implement Disappearance (ID):", "probabilityID")
    ]

    entries = {}

    for idx, (label_text, var_name) in enumerate(fields):
        ttk.Label(main_frame, text=label_text, style="TLabel").grid(row=idx, column=0, padx=10, pady=5, sticky="w")
        entry = ttk.Entry(main_frame)
        entry.grid(row=idx, column=1, padx=10, pady=5)
        entry.insert(0, config.get(var_name, ""))
        entries[var_name] = entry

    num_implements_entry = entries["num_implements"]
    num_tasks_entry = entries["num_tasks"]
    num_vehicles_entry = entries["num_vehicles"]
    dataset_entry = entries["seed"]
    time = entries["time_horizon"]
    periods = entries["num_periods"]
    probabilityTA_entry = entries["probabilityTA"]
    probabilityTD_entry = entries["probabilityTD"]
    probabilityVA_entry = entries["probabilityVA"]
    probabilityVD_entry = entries["probabilityVD"]
    probabilityIA_entry = entries["probabilityIA"]
    probabilityID_entry = entries["probabilityID"]

    full_var = tk.BooleanVar()
    full_checkbox = ttk.Checkbutton(main_frame, text="Full", variable=full_var)
    full_checkbox.grid(row=len(fields), column=0, columnspan=2, pady=10)
    full_var.set(config.get("full", False))

    run_button = ttk.Button(main_frame, text="Run Optimization", command=run_optimization, style="TButton")
    run_button.grid(row=len(fields) + 1, column=0, columnspan=2, pady=20)

    root.mainloop()

root = tk.Tk()
root.title("Choose Mode")
root.geometry("800x600")
root.configure(bg="white")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton",
                font=("Roboto", 14, "bold"),
                background="#b3b3b3",
                foreground="black")

header_frame = tk.Frame(root, bg="white")
header_frame.pack(fill=tk.X, pady=10)

logo1_image = Image.open("Logos/URJC-Logo.png")
logo1_image = logo1_image.resize((192, 108), Image.ANTIALIAS)
logo1_photo = ImageTk.PhotoImage(logo1_image)
logo1_label = tk.Label(header_frame, image=logo1_photo, bg="white")
logo1_label.image = logo1_photo
logo1_label.pack(side=tk.LEFT, padx=10)

title_label = tk.Label(header_frame, text="Select Mode", font=("Roboto", 20, "bold"), bg="white", fg="black")
title_label.pack(side=tk.LEFT, expand=True, padx=10)

logo2_image = Image.open("Logos/Logo-Universita-Roma-Tor-Vergata.png")
logo2_image = logo2_image.resize((192, 50), Image.ANTIALIAS)
logo2_photo = ImageTk.PhotoImage(logo2_image)
logo2_label = tk.Label(header_frame, image=logo2_photo, bg="white")
logo2_label.image = logo2_photo
logo2_label.pack(side=tk.RIGHT, padx=10)

main_frame = tk.Frame(root, bg="white")
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

tk.Label(main_frame, text="Select how you want to proceed:", font=("Roboto", 16), bg="white", fg="black").pack(pady=20)

manual_button = ttk.Button(main_frame, text="Manual Parameter Entry", command=manual_entry, style="TButton")
manual_button.pack(pady=10)

file_button = ttk.Button(main_frame, text="Load Configuration File", command=load_file, style="TButton")
file_button.pack(pady=10)

root.mainloop()
