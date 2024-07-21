 

def TrueObj ():
    pass

def AssignmentDone (AssignmentT):
    try:
        Assigment={}
        Assigment['x_'+str(AssignmentT[0][0])+"_"+str(AssignmentT[0][1])+"_"+str(AssignmentT[0][2])]=1
        return Assigment
    except:
        print("Other event happen")

