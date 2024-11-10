from move_base_msgs.msg import MoveBaseAction
import sys
import time
import actionlib
from math import sqrt
import numpy as np
import rospy 
from queue import SimpleQueue
import rospy
from move_base_msgs.msg import MoveBaseAction,MoveBaseGoal
from sensor_msgs.msg import Image
from geometry_msgs.msg import PolygonStamped
import cv2 as cv
import cv_bridge as cvb

Event = [False, "", 0]

if Event[0]==False:
    print("Event triggered")