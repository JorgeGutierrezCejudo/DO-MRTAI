def CompleteCompatibility(num_implements,num_tasks,num_vehicles,IK,VI,KV):
  
    KI = [[] for _ in range(num_implements)]
    IV=[[] for _ in range(num_vehicles)]
    VK=[[] for _ in range(num_tasks)]
    KV=[[] for _ in range(num_vehicles)]


    for k in range(num_tasks):
        for i in IK[k]:
            KI[i].append(k)

    for i in range(num_implements):
        for v in VI[i]:
            IV[v].append(i)
        


    # for k in range(num_tasks):
    #     for i in IK[k]:
    #         for v in VI[i]:
    #             if v  not in VK[k]:
    #                 VK[k].append(v)

            
    for k in range(num_tasks):
        for v in VK[k]:
            KV[v].append(k)

    VK=[[] for _ in range(num_tasks)]

    for v in range(num_vehicles):
        for k in KV[v]:
            VK[k].append(v)

    return KI,IV,KV,VK