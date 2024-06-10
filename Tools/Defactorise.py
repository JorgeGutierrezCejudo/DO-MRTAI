import numpy as np

def XAsignmentsDefactorise(Asignments):
    A_implements = []
    A_tasks = []
    A_vehicles = []
    if Asignments:
        for key, value in Asignments.items():
            _, i, j, k = key.split('_')
            A_implements.append(int(i))
            A_tasks.append(int(j))
            A_vehicles.append(int(k))

    return A_implements, A_tasks, A_vehicles

def ZAsignmentsDefactorise(Asignments):
    A_vehiclesd = []
    if Asignments:
        for key, value in Asignments.items():
            _, i = key.split('_')
            A_vehiclesd.append(int(i))

    return A_vehiclesd

def TEXAsignmentsDefactorise(Asignments):
    A_implements = []
    A_tasks = []
    A_vehicles = []
    A_periods = []
    if Asignments:
        for key, value in Asignments.items():
            _, i, j, k ,t= key.split('_')
            A_implements.append(int(i))
            A_tasks.append(int(j))
            A_vehicles.append(int(k))
            A_periods.append(int(t))

    return A_implements, A_tasks, A_vehicles, A_periods

def TEZAsignmentsDefactorise(Asignments):
    A_vehiclesd = []
    A_periodsD = []
    if Asignments:
        for key, value in Asignments.items():
            _, i, t = key.split('_')
            A_vehiclesd.append(int(i))
            A_periodsD.append(int(t))

    return A_vehiclesd, A_periodsD

def TInfo(Asignments,num_vehicles,num_periods):
    Tinfo=np.zeros((num_vehicles,num_periods))
    if Asignments:
        for clave, valor in Asignments.items():
            partes = clave.split('_')
            i = int(partes[1])
            j = int(partes[2])
            Tinfo[i, j] =int(valor)

    return Tinfo





