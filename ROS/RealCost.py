#!/usr/bin/env python


import rospy
from nav_msgs.srv import GetPlan
from geometry_msgs.msg import PoseStamped
import math
import sys
import time
import actionlib
import numpy as np
from Tools import Defactorise as df


def RealCost(Asignation,Implements,Tasks,Vehicles,CostEstimation):
    real_cost=np.zeros(len(Asignation))
    Error=np.zeros(len(Asignation))

    for i in range(len(Asignation)):
        A_implements, A_tasks, A_vehicles=df.XAsignmentsDefactorise(Asignation)

        xinit = Vehicles[A_vehicles[i],0]
        yinit = Vehicles[A_vehicles[i],1]
        ximplement = Implements[A_implements[i],0]
        yimplement = Implements[A_implements[i],1]
        xgoal = Tasks[A_tasks[i],0]
        ygoal = Tasks[A_tasks[i],1]

        # Create service client
        client = rospy.ServiceProxy('robot_0/move_base/make_plan', GetPlan)

        # Create request message
        start = PoseStamped()
        start.header.frame_id = "map"
        start.pose.position.x = xinit
        start.pose.position.y = yinit
        start.pose.orientation.w = 0.0
        goal = PoseStamped()
        goal.header.frame_id = "map"
        goal.pose.position.x = ximplement
        goal.pose.position.y = yimplement
        goal.pose.orientation.w = 0.0
        tolerance = 1
        
        # Call service
        try:
            response = client(start,goal, tolerance)
            # Print response message
            rospy.loginfo("Got plan with %d waypoints.", len(response.plan.poses))
        except rospy.ServiceException as e:
            rospy.logerr("Failed to call service /move_base/make_plan: %s",)

        VehicleImplemtDistance = 0
        for j in range(1, len(response.plan.poses)):
            P1=response.plan.poses[j-1]
            P2=response.plan.poses[j]
            x1, y1 = P1.pose.position.x, P1.pose.position.y
            x2, y2 = P2.pose.position.x, P2.pose.position.y
            VehicleImplemtDistance += math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # Create request message
        start = PoseStamped()
        start.header.frame_id = "map"
        start.pose.position.x = ximplement
        start.pose.position.y = yimplement
        start.pose.orientation.w = 0.0
        goal = PoseStamped()
        goal.header.frame_id = "map"
        goal.pose.position.x = xgoal
        goal.pose.position.y = ygoal
        goal.pose.orientation.w = 0.0
        tolerance = 1
        
        # Call service
        try:
            response = client(start,goal, tolerance)
        except rospy.ServiceException as e:
            rospy.logerr("Failed to call service /move_base/make_plan: %s",)

        taskImplemtDistance = 0
        for k in range(1, len(response.plan.poses)):
            P1=response.plan.poses[k-1]
            P2=response.plan.poses[k]
            x1, y1 = P1.pose.position.x, P1.pose.position.y
            x2, y2 = P2.pose.position.x, P2.pose.position.y
            taskImplemtDistance += math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        
        real_cost[i] = VehicleImplemtDistance + taskImplemtDistance

        Diference = abs(CostEstimation[A_implements[i],A_tasks[i],A_vehicles[i]] - real_cost[i])
        Error[i] = Diference / CostEstimation[A_implements[i],A_tasks[i],A_vehicles[i]]

    for i in range(len(Asignation)):
        if Error[i] > 0.1:
            print("The error is greater than 10 for the cost of",A_vehicles[i])
            CostEstimation[A_implements[i],A_tasks[i],A_vehicles[i]] = real_cost[i]
            Errors = 10
            break
        
        else:
            print("Good estimation for the cost of",A_vehicles[i])
            print("The real cost is",real_cost[i],"and the estimated cost is",CostEstimation[A_implements[i],A_tasks[i],A_vehicles[i]])
            Errors=0
    return Errors,CostEstimation
        
    
    





