import modern_robotics as mr
import math
import numpy as np

# Definimos las variables
pi = math.pi
o = [-pi/2, pi/2, pi/3, -pi/4, 1, pi/6]
M = [[1, 0, 0, 3.7320],
     [0, 1, 0, 0],
     [0, 0, 1, 2.7320],
     [0, 0, 0, 1]]
S = [[0, 0, 0, 0, 0, 0],
     [0, 1, 1, 1, 0, 0],
     [1, 0, 0, 0, 0, 1],
     [0, 0, 1, -0.732, 0, 0],
     [-1, 0, 0, 0, 0, -3.732],
     [0, 1, 2.732, 3.732, 1, 0]]
B = [[0, 0, 0, 0, 0, 0],
     [0, 1, 1, 1, 0, 0],
     [1, 0, 0, 0, 0, 1],
     [0, 2.732, 3.732, 2, 0, 0],
     [2.732, 0, 0, 0, 0, 0],
     [0, -2.732, -1, 0, 1, 0]]
M=np.array(M).T
B=np.array(B).T
S=np.array(S).T
o = np.array(o).T

# Resolvemos la pregunta 4 usando FKinSpace
T_space = mr.FKinSpace(M, S, o)

# Resolvemos la pregunta 5 usando FKinBody
T_body = mr.FKinBody(M, B, o)

# Imprimimos los resultados redondeados a 3 decimales
print("Pregunta 4:")
print(np.round(T_space, 3))
print("Pregunta 5:")
print(np.round(T_body, 3).T)
