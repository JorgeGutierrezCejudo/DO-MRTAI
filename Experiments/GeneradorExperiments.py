import json

experiments = []

for num_vehicles in range(10, 101, 10):  # de 10 a 50 
    for num_periods in range(2, 5):  # de 1 a 6
        for num_tasks in range(num_vehicles*num_periods, 101, 10):  
            for seed in range(1, 7):  # semillas de 1 a 6
                experiment = {
                    "num_implements": str(num_vehicles),  # mismo número que vehículos
                    "num_tasks": str(num_tasks),
                    "num_vehicles": str(num_vehicles),
                    "seed": str(seed),
                    "full": True,
                    "time_horizon": "2000",
                    "num_periods": str(num_periods),
                    "probabilityTA": "0",
                    "probabilityTD": "0",
                    "probabilityVA": "0",
                    "probabilityVD": "0",
                    "probabilityIA": "0",
                    "probabilityID": "0"
                }
                experiments.append(experiment)

# Guardar a JSON
with open("experimentos_ordenados.json", "w") as f:
    json.dump(experiments, f, indent=4)

print(f"✅ Generados {len(experiments)} experimentos.")
