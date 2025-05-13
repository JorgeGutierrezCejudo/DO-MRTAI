A={'0': {'TaskCount': 1, 'Tasks': [{'Implement': '8', 'Task': '6'}]}, '1': {'TaskCount': 2, 'Tasks': [{'Implement': '1', 'Task': '4'}, {'Implement': '1', 'Task': '2'}]}, '2': {'TaskCount': 1, 'Tasks': [{'Implement': '9', 'Task': '1'}]}, '4': {'TaskCount': 3, 'Tasks': [{'Implement': '6', 'Task': '0'}, {'Implement': '6', 'Task': '5'}, {'Implement': '6', 'Task': '3'}]}}

for i in A.keys():
    Robot = i
    print(i)
    for j in A[i]["Tasks"]:
        print("Implement",j["Implement"])
        print("Task",j["Task"])
