
def TrueObj (Distancia,TaskNotDonne,t,M):
    obj=0
    CostPenalty=0
    M=TaskNotDonne[:,3]
    for i in range(len(TaskNotDonne)):
        CostPenalty=M[i]*t/100+CostPenalty
    print("CostPenalty",CostPenalty)

    for i in range(len(Distancia)):
        obj+=Distancia[i]
    obj+=CostPenalty
    return obj


def AssignmentDone (AssignmentT):
    try:
        Assigment={}
        Assigment['x_'+str(AssignmentT[0][0])+"_"+str(AssignmentT[0][1])+"_"+str(AssignmentT[0][2])]=1
        return Assigment
    except:
        print("Other event happen")

