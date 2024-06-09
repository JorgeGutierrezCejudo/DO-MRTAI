import pandas as pd
import time
import os

def CreateResults(model,num_implements,num_tasks,num_vehicles,alpha,beta,gamma):
# Write the DataFrame to the CSV file with an index column
    Day=time.strftime("%d-%m-%y")
    Time=time.strftime("%H:%M:%S")
    Dir="Exp"+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+"_"+str(Day)+"_"+str(Time)+"_"+str(alpha)+","+str(beta)+","+str(gamma)
    os.makedirs('Result/'+Dir)
    os.chdir('Result/'+Dir)
    
    model.write("3index-assignment.lp")
    model.write("solution.sol")

    all_vars = model.getVars()
    values = model.getAttr("X", all_vars)
    names = model.getAttr("VarName", all_vars)

    tot_var = {name: val for name,val in zip(names, values) if val>0}


    df = pd.DataFrame({'Result: Index('+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+") Weigth("+str(alpha)+","+str(beta)+","+str(gamma)+"),Runtime("+str(model.Runtime)+"),Objetive("+str(round(model.ObjVal,5))+"),GAP("+str(round(model.MIPGap,6))+")": tot_var.keys()})
    df.to_csv("Alocation Result-"+str(num_implements)+","+str(num_tasks)+","+str(num_vehicles)+".csv", mode='a', header=True, index= False)