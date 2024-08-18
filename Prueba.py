InfoTaskDone = []  # Inicializa una lista vacía para almacenar las tareas completadas

# Suponiendo que 'M[AssignmentT[0][1]]' es el valor de la penalización y 't' es el tiempo
task_info = {
    "PenaltyValue": 2,
    "Time": 2
}

# Añadir el diccionario de la tarea completada a la lista
InfoTaskDone.append(task_info)


task_info = {
    "PenaltyValue": 3,
    "Time": 2
}

InfoTaskDone.append(task_info)




penalty_values = [task["Time"] for task in InfoTaskDone]
print("Penalty values:", penalty_values)