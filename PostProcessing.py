
def TrueObj(Distancia, TaskNotDone, t, M,InfoTaskDone):
    CostPenalty = 0
    CostDistance = 0
    DoneAsignationCost = 0

    M = TaskNotDone[:, 3]
    for i in range(len(TaskNotDone)):
        CostPenalty += M[i] * t / 100
    
    penalty_values = [task["Penalty"] for task in InfoTaskDone]
    time_values = [task["Time"] for task in InfoTaskDone]

    for i in range(len(penalty_values)):
        DoneAsignationCost += penalty_values[i] * time_values[i]/100

    for i in range(len(Distancia)):
        CostDistance += Distancia[i]
    
    
    return CostPenalty,DoneAsignationCost,CostDistance




def AssignmentDone (AssignmentT,t,InfoTaskDone,M,depot_info):
    if AssignmentT or depot_info:
        print("Dentro")
        Assigment={}
        ZAssigment={}
        for i in range(len(AssignmentT)):
            key = 'x_' + str(AssignmentT[i][0]) + "_" + str(AssignmentT[i][1]) + "_" + str(AssignmentT[i][2]) + "_" + str(AssignmentT[i][3])
            Assigment[key] = 1 
            try: 
                task_info = {
                "Penalty": M[AssignmentT[i][3]][AssignmentT[i][1]],
                "Time": t
                }
            except:
                task_info = {
                "Penalty": M[AssignmentT[i][1]],
                "Time": t
                }

            InfoTaskDone.append(task_info)
        for i in range (len(depot_info)):
            key='z_'+str(depot_info[0][0])+"_"+str(depot_info[0][1])
            ZAssigment[key]=1
        return Assigment,InfoTaskDone,ZAssigment
    else:
        return None,InfoTaskDone,None

