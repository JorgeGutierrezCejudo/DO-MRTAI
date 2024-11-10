import roslibpy
from nav_msgs.srv import GetPlan
from geometry_msgs.msg import PoseStamped
import math
import sys
import time
import numpy as np
from Tools import Defactorise as df


client=roslibpy.Ros(host="192.168.1.54",port=9090)
client.run()
print("Conected with ROS?")


xinit =10
yinit = 5
ximplement = 30 
yimplement = 5

# Create service client
service = roslibpy.Service(client,'robot_0/move_base/make_plan', "nav_msgs/GetPlan")
get_plan_request = {
    "start": {
        "header": {
            "seq": 0,
            "stamp": {
                "secs": 0,
                "nsecs": 0
            },
            "frame_id": "map"
        },
        "pose": {
            "position": {
                "x": xinit,
                "y": yinit,
                "z": 0.0
            },
            "orientation": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "w": 1.0
            }
        }
    },
    "goal": {
        "header": {
            "seq": 0,
            "stamp": {
                "secs": 0,
                "nsecs": 0
            },
            "frame_id": "map"
        },
        "pose": {
            "position": {
                "x": ximplement,
                "y": yimplement,
                "z": 0.0
            },
            "orientation": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0,
                "w": 1.0
            }
        }
    },
    "tolerance": 0.0
}
request=roslibpy.ServiceRequest(get_plan_request)

        
        # Call service

response = service.call(request)


def calculate_distance(p1, p2):
    return math.sqrt((p2["x"] - p1["x"])**2 + (p2["y"] - p1["y"])**2)

# Obtener las poses
poses = response["plan"]["poses"]

# Extraer las posiciones y calcular la distancia total
total_distance = 0.0
for i in range(len(poses) - 1):
    p1 = poses[i]["pose"]["position"]
    p2 = poses[i + 1]["pose"]["position"]
    total_distance += calculate_distance(p1, p2)

print(f"Distancia total recorrida: {total_distance:.2f} metros")

client.terminate

# VehicleImplemtDistance = 0
# for j in range(1, len(response.plan.poses)):
#     P1=response.plan.poses[j-1]
#     P2=response.plan.poses[j]
#     x1, y1 = P1.pose.position.x, P1.pose.position.y
#     x2, y2 = P2.pose.position.x, P2.pose.position.y
#     VehicleImplemtDistance += math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# print("Distanci",VehicleImplemtDistance)
        