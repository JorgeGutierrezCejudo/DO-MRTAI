import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import os
import json
import csv
from Data import Data 
from Algorithm import DoMRTAI as dm
import subprocess 

# Directorio y balance de costos y energía
CostBalance = [1, 0.01]  # [Costo de estático, Costo de dinámico]
EnergyBalance = [1, 0.2] # [Energía de estático, Energía de dinámico]

# Archivo de configuración
default_config_file = "ConfigFile/config.json"
dir=os.getcwd()

# Crear carpeta de resultados
results_dir = "Results"
os.makedirs(results_dir, exist_ok=True)


# Archivo CSV de resultados
csv_file = os.path.join(results_dir, "Results.csv")

# Definir encabezados del CSV
csv_headers = [
    "num_implements", "num_tasks", "num_vehicles", "seed", "full", 
    "time_horizon", "num_periods", "probabilityTA", "probabilityTD",
    "probabilityVA", "probabilityVD", "probabilityIA", "probabilityID",
    "t", "toptimization", "Obj","PenaltyCost","StaticCost", "DistanciaTotal","Distancia_list","DesvDistancia","TaskDone_list","DesvTaskDone",
]

# Verificar si el archivo CSV existe, si no, crearlo con encabezados
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline='') as f:
        writer = csv.writer(f,delimiter=";")
        writer.writerow(csv_headers)

def save_results_to_csv(experiment, t,toptimization,Obj,DoneAsignationCost,StaticCostTask,Distancia_list,InfoTaskDone):
    Distancia_list = [item[1] for item in Distancia_list]
    DistanciaTotal= sum(Distancia_list)
    DesvDistancia=max(Distancia_list) - min(Distancia_list)
    InfoTaskDone = [item[1] for item in InfoTaskDone]
    DesvTaskDone= max(InfoTaskDone) - min(InfoTaskDone)
    with open(csv_file, "a", newline='') as f:
        writer = csv.writer(f,delimiter=";")
        writer.writerow([
            experiment["num_implements"], experiment["num_tasks"], experiment["num_vehicles"], 
            experiment["seed"], experiment["full"], experiment["time_horizon"], 
            experiment["num_periods"], experiment["probabilityTA"], experiment["probabilityTD"],
            experiment["probabilityVA"], experiment["probabilityVD"], experiment["probabilityIA"], 
            experiment["probabilityID"], t, toptimization, Obj,DoneAsignationCost,StaticCostTask,DistanciaTotal,Distancia_list,DesvDistancia,InfoTaskDone,DesvTaskDone
        ])


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

def run_experiment(experiment):
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
    """ Ejecuta múltiples experimentos desde un archivo JSON y guarda resultados en un CSV único. """
    with open(config_file, 'r') as f:
        experiments = json.load(f)

    visualization_process = subprocess.Popen(["python3.8", "View/Result.py"])

    for experiment in experiments:
        run_experiment(experiment)


def manual_entry():
    root.destroy()
    run_manual_configuration()


def load_file():
    file_path = filedialog.askopenfilename(title="Select JSON Configuration File", filetypes=[("JSON Files", "*.json")])
    if file_path:
        run_experiment_from_file(file_path)


def run_manual_configuration():
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
