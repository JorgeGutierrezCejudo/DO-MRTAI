#!/usr/bin/env python

import roslibpy
import math
import numpy as np
from Tools import Defactorise as df


def calculate_distance(p1, p2):
    """Calcula la distancia euclidiana entre dos puntos."""
    return math.sqrt((p2["x"] - p1["x"])**2 + (p2["y"] - p1["y"])**2)


def get_plan_distance(client, service_name, start_pose, goal_pose, tolerance):
    """
    Llama al servicio de planificación y calcula la distancia total del plan.
    
    Args:
        client: Cliente ROS conectado.
        service_name: Nombre del servicio para llamar.
        start_pose: Pose inicial en formato de diccionario.
        goal_pose: Pose objetivo en formato de diccionario.
        tolerance: Tolerancia en el cálculo del plan.
        
    Returns:
        Distancia total del recorrido planificado.
    """
    service = roslibpy.Service(client, service_name, "nav_msgs/GetPlan")
    get_plan_request = {
        "start": {
            "header": {
                "seq": 0,
                "stamp": {"secs": 0, "nsecs": 0},
                "frame_id": "map"
            },
            "pose": start_pose
        },
        "goal": {
            "header": {
                "seq": 0,
                "stamp": {"secs": 0, "nsecs": 0},
                "frame_id": "map"
            },
            "pose": goal_pose
        },
        "tolerance": tolerance
    }

    request = roslibpy.ServiceRequest(get_plan_request)
    response = service.call(request)
    
    poses = response["plan"]["poses"]
    total_distance = 0.0
    for i in range(len(poses) - 1):
        p1 = poses[i]["pose"]["position"]
        p2 = poses[i + 1]["pose"]["position"]
        total_distance += calculate_distance(p1, p2)
    
    return total_distance


def RealCost(Asignation, Implements, Tasks, Vehicles, CostEstimation,client):
    """
    Calcula el costo real y el error para las asignaciones de vehículos, implementos y tareas.
    
    Args:
        Asignation: Matriz de asignaciones.
        Implements: Coordenadas de los implementos.
        Tasks: Coordenadas de las tareas.
        Vehicles: Coordenadas iniciales de los vehículos.
        CostEstimation: Estimación de costos.
        
    Returns:
        Tuple de errores y la matriz de estimaciones actualizada.
    """
    real_cost = np.zeros(len(Asignation))
    Error = np.zeros(len(Asignation))
    
    for i in range(len(Asignation)):
        A_implements, A_tasks, A_vehicles = df.XAsignmentsDefactorise(Asignation)

        # Poses iniciales, de implementos y tareas
        start_pose = {
            "position": {"x": Vehicles[A_vehicles[i], 0], "y": Vehicles[A_vehicles[i], 1], "z": 0.0},
            "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
        }
        implement_pose = {
            "position": {"x": Implements[A_implements[i], 0], "y": Implements[A_implements[i], 1], "z": 0.0},
            "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
        }
        task_pose = {
            "position": {"x": Tasks[A_tasks[i], 0], "y": Tasks[A_tasks[i], 1], "z": 0.0},
            "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}
        }

        # Distancia vehículo a implemento
        vehicle_to_implement_distance = get_plan_distance(client, 'robot_0/move_base/make_plan', start_pose, implement_pose, 1.0)
        
        # Distancia implemento a tarea
        implement_to_task_distance = get_plan_distance(client, 'robot_0/move_base/make_plan', implement_pose, task_pose, 1.0)

        # Costo real y error
        real_cost[i] = vehicle_to_implement_distance + implement_to_task_distance
        estimated_cost = CostEstimation[A_implements[i], A_tasks[i], A_vehicles[i]]
        Difference = abs(estimated_cost - real_cost[i])
        Error[i] = Difference / estimated_cost

    # Actualización de costos y manejo de errores
    for i in range(len(Asignation)):
        if Error[i] > 0.1:
            print(f"The error is greater than 10% for the cost of vehicle {A_vehicles[i]}")
            CostEstimation[A_implements[i], A_tasks[i], A_vehicles[i]] = real_cost[i]
            Errors = 10
            break
        else:
            print(f"Good estimation for the cost of vehicle {A_vehicles[i]}")
            print(f"The real cost is {real_cost[i]:.2f} and the estimated cost is {CostEstimation[A_implements[i], A_tasks[i], A_vehicles[i]]:.2f}")
            Errors = 0
    
    return Errors, CostEstimation
