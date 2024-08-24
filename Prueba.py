import numpy as np

data = 1
num = 1
Vehicles = np.array([[56.26390165, 28.34456164, 0.89, 10, 73.99516129],
                     [89.79634926, 43.70288105, 0.95, 100, 82.174375],
                     [66.2856118, 18.50791373, 0.84, 100, 83.93181818]])

# Generación del nuevo vehículo
np.random.seed(data + 20)
Vehicle = np.random.randint(0, 100, size=(num, 2))
EfVehicle = np.random.randint(80, 100, size=(num, 1)) / 100
Vehicle = np.concatenate((Vehicle, EfVehicle), axis=1)

np.random.seed(data + 1)
T_max = np.random.randint(100, 101, size=(num, 1))
Vehicle = np.concatenate((Vehicle, T_max), axis=1)

np.random.seed(data)
That = [np.random.randint(int(0.75 * T_max[i]), T_max[i]) for i in range(num)]
That = np.array(That).reshape(num, 1)
Vehicle = np.concatenate((Vehicle, That), axis=1)

# Concatenar el nuevo vehículo a la lista de vehículos existente
Vehicles = np.concatenate((Vehicles, Vehicle), axis=0)

print(Vehicles)