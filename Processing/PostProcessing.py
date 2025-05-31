import math

def TrueObj(Distancia, InfoTaskDone, RobotPerformance,vehicle,task,implement):
    """
    Calculates the total costs associated with penalties, distances, and completed task assignments.

    Args:
        Distancia (list): List of distances traveled.
        InfoTaskDone (list): List of dictionaries containing information about completed tasks, 
                             with keys "Penalty" and "Time".
        RobotPerformance (list): List of dictionaries containing information about robot performance,
        vehicles (list): List of all information about vehicles.
        task (list): List of all information about tasks.
        implement (list): List of all information about implements.

    Returns:
        Obj (float): The total cost, which is the sum of the distance costs and the penalty costs for completed tasks.

    """
    CostStaticTask = 0  # Initialize the penalty cost for uncompleted tasks
    CostDistance = 0  # Initialize the cost for distances traveled
    DoneAsignationCost = 0  # Initialize the cost for completed task assignments
    # Extract penalty and time values for completed tasks
    penalty_values = [task["Penalty"] for task in InfoTaskDone]
    time_values = [task["Time"] for task in InfoTaskDone]

    # Calculate the cost for completed task assignments
    for i in range(len(penalty_values)):
        #DoneAsignationCost += (0.02*(time_values[i]*time_values[i])) + penalty_values[i] 
        DoneAsignationCost += (200*(math.log10(time_values[i])))+ penalty_values[i] 
        
    for i in RobotPerformance.keys():
        for j in RobotPerformance[i]["Tasks"]:
            CostStaticTask += (task[int(j["Task"])]/(vehicle[int(i)]*implement[int(j["Implement"])]))  

    # Calculate the total cost for distances traveled
    CostDistance = sum(Distancia)
 

    # Return the calculated costs
    return CostDistance,DoneAsignationCost,CostStaticTask 

def AssignmentDone(AssignmentT, t, InfoTaskDone, M, depot_info):
    """
    Processes task assignments and depot information, generating dictionaries to track completed assignments
    and updating a list with task details.

    Args:
        AssignmentT (list): List of task assignments, where each task is represented as a list or tuple of values.
        t (int/float): A timestamp or time value associated with the tasks.
        InfoTaskDone (list): A list that stores information about completed tasks.
        M (list or matrix): A matrix or data structure used to calculate penalties for tasks.
        depot_info (list): A list of depot-related information.

    Returns:
        tuple: A tuple containing:
            - Assigment (dict): Dictionary of task assignments with keys in the format 'x_<values>'.
            - InfoTaskDone (list): Updated list of completed task information.
            - ZAssigment (dict): Dictionary of depot-related assignments with keys in the format 'z_<values>'.
    """
    if AssignmentT or depot_info:  # Check if there are any task assignments or depot information
        Assigment = {}  # Dictionary to store task assignments
        ZAssigment = {}  # Dictionary to store depot-related assignments

        # Process each task in AssignmentT
        for i in range(len(AssignmentT)):
            # Generate a key for the task in the format 'x_<values>'
            key = 'x_' + str(AssignmentT[i][0]) + "_" + str(AssignmentT[i][1]) + "_" + str(AssignmentT[i][2]) + "_" + str(AssignmentT[i][3])
            Assigment[key] = 1  # Mark the task as completed in the Assigment dictionary

            # Try to calculate the penalty using the matrix M
            try:
                task_info = {
                    "Penalty": M[AssignmentT[i][3]][AssignmentT[i][1]],  # Penalty based on task indices
                    "Time": AssignmentT[i][4] # Time associated with the task
                }
            except:  # Handle cases where the indices are invalid or missing
                task_info = {
                    "Penalty": M[AssignmentT[i][1]],  # Fallback penalty calculation
                    "Time": AssignmentT[i][4]  # Time associated with the task
                }

            # Append the task information to the InfoTaskDone list
            InfoTaskDone.append(task_info)

        # Process each depot in depot_info
        for i in range(len(depot_info)):
            # Generate a key for the depot in the format 'z_<values>'
            key = 'z_' + str(depot_info[0][0]) + "_" + str(depot_info[0][1])
            ZAssigment[key] = 1  # Mark the depot as completed in the ZAssigment dictionary

        # Return the dictionaries and the updated InfoTaskDone list
        return Assigment, InfoTaskDone, ZAssigment
    else:
        # If no assignments or depot information, return None for the dictionaries and the unchanged InfoTaskDone
        return None, InfoTaskDone, None


def AssignmentByRobot(Assignments):
    """
    Processes the assignments, organizes the tasks performed by each vehicle, 
    and counts the number of tasks performed by each vehicle.

    Args:
        Assignments (list): Either:
            - A list of dictionaries with keys in the format 'X_implement_task_vehicle[_period]'
              and values indicating whether the assignment is active ('1') or not ('0'), or
            - A list of strings representing active assignments directly.

    Returns:
        dict: Dictionary where the keys are the vehicle identifiers and the values
              include the number of tasks and a list of tasks performed by each vehicle.
    """
    if Assignments is None:
        return None
    else:
        tasks_by_vehicle = {}

        # If it's a list of strings (active keys), wrap them in a dictionary format
        if all(isinstance(item, str) for item in Assignments):
            Assignments = [{key: '1'} for key in Assignments]
        for assignment in Assignments:
            if not isinstance(assignment, dict):
                raise TypeError(f"Expected each element to be a dictionary or a list of strings, but got {type(assignment).__name__}")

            for key, value in assignment.items():

                parts = key.split('_')
                implement = parts[1]
                task = parts[2]
                vehicle = parts[3]

                if vehicle not in tasks_by_vehicle:
                    tasks_by_vehicle[vehicle] = {
                        "TaskCount": 0,
                        "Tasks": []
                    }

                tasks_by_vehicle[vehicle]["Tasks"].append({
                    "Implement": implement,
                    "Task": task
                })
                tasks_by_vehicle[vehicle]["TaskCount"] += 1
        tasks_by_vehicle = dict(sorted(tasks_by_vehicle.items(), key=lambda x: int(x[0])))
        return tasks_by_vehicle
