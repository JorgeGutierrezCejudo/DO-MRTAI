
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






def AssignmentDone (AssignmentT,t,InfoTaskDone,M):
    try:
        Assigment={}
        Assigment['x_'+str(AssignmentT[0][0])+"_"+str(AssignmentT[0][1])+"_"+str(AssignmentT[0][2])]=1
        task_info = {
        "Penalty": M[AssignmentT[0][1]],
        "Time": t
        }
        InfoTaskDone.append(task_info)
        return Assigment,InfoTaskDone
    except:
        return None,InfoTaskDone

