#!/usr/bin/python
from pulp import *
import numpy as np
import random
import time

t_avg=[]
for n in [10,20]:
    for m in [4,8,12]:
        t=[]
        for times in range(20):
            node = n
            video_number = m

            input_number = [0 for i in range(node-1)] # 不包括server

            for i in range(len(input_number)):
                input_number[i] = random.randint(1,i+1) # ex:第3個節點的進入點可能有1~3個

            node_t = []
            node_r = []
            upstream = []
            for i in range(len(input_number)):
                upstream.append(np.random.choice(range(i+1), input_number[i], False)) # 分別決定每個節點(不包括server)有哪些上游節點

            for i in range(node-1):
                for j in range(len(upstream)):
                    upstream[j] = list(upstream[j])
                    if upstream[j].count(i) > 0:
                        node_t.append(i)
                        node_r.append(j+1)
                    else:
                        continue

            #node_t = [0,0,0,1,1,2,2,3,3,4,4,5,6,7,7,7,9]
            #node_r = [1,2,3,2,3,4,9,4,5,5,7,6,8,8,9,10,10]

            #b = [5,4,3,2,6,4,5,1,2,7,3,1,6,5,7,3,4]
            #video = [[3,2,2,2,2,1,1,1,1,1,1,1,2,3,3,2,1],[2,2,3,2,3,4,4,1,1,1,1,1,2,1,1,3,1],[2,2,2,2,2,2,2,1,1,1,1,2,3,1,2,1,3],[2,2,2,2,2,2,2,1,1,1,1,1,1,3,3,2,1],[2,2,2,2,2,2,2,1,1,1,1,1,1,3,3,2,1],[2,2,2,2,2,2,2,1,1,1,1,1,1,3,3,2,1],[2,2,2,2,2,2,2,1,1,1,1,1,1,3,3,2,1],[2,2,2,2,2,2,2,1,1,1,1,1,1,3,3,2,1]]
            b = [0 for _ in range(len(node_r))]
            for i in range(len(node_r)):
                b[i] = random.randint(1, video_number-1)
            #random number of video in every node
            video = [[0 for _ in range(len(node_r))] for _ in range(video_number)]
            for i in range(video_number):
                for j in range(len(node_r)):
                    video[i][j] = random.randint(0,20)

            '''
            node = 9
            node_t = [0,0,0,1,1,2,3,3,4,4,5,6,7]
            node_r = [1,2,3,2,3,4,4,5,5,7,6,8,8]
            b = [2,1,1,1,2,2,1,1,1,1,1,1,1]
            video = [[3,2,2,2,2,1,1,1,1,1,1,1,1],[2,2,3,2,3,4,4,1,1,1,1,1,1],[2,2,2,2,2,2,2,1,1,1,1,1,1]]
            '''
            '''
            node = 5
            video_number=3
            node_t = [0,0,0,1,1,2,3]
            node_r = [1,2,3,2,3,4,4]
            b = [2,1,1,1,2,2,1]
            video = [[3,2,2,2,2,1,1],[2,2,2,2,3,4,4],[2,2,2,2,2,2,2]]
            '''
            '''
            node = 2
            node_t = [0]
            node_r = [1]
            b = [3]
            video = [[0],[0],[2]]
            '''
            count = [0 for _ in range(node)]
            edge = []
            node_in = []
            node_out = []
            count_in = [0 for _ in range(node)]
            count_out = [0 for _ in range(node)]

            for i in range(1,node):
                for j in range(len(node_r)):
                    if(node_r[j] == i):
                        count[i] += 1
            for i in range(len(count)):
                if(count[i]>1):
                    for j in range(len(node_r)):
                        if(node_r[j]==i):
                            edge.append(j)
            #print(edge)
            #print(count)
            for i in range(1,node):
                for j in range(len(node_r)):
                    if(node_r[j] == i):
                        node_in.append(j)
                        count_in[i] += 1

            for i in range(1,node):
                for j in range(len(node_t)):
                    if(node_t[j] == i):
                        node_out.append(j)
                        count_out[i] += 1



            #creat a problem
            prob = LpProblem("The Maximize：", LpMaximize)

            #creat a set to store the decision variable
            edge_right =[[' ' for _ in range(len(node_t))] for _ in range(video_number)]
            for i in range(video_number):
                for j in range(len(node_t)):
                    edge_right[i][j] = LpVariable("video%d_e%dto%d"%(i+1,node_t[j],node_r[j]),cat="Binary")

            #object
            prob += lpSum([[edge_right[i][j]*video[i][j] for j in range(len(node_t))]for i in range(video_number)])

            #Constraints

            for k in range(len(b)):
                prob += lpSum([edge_right[i][k] for i in range(video_number)]) <= b[k]

            #不要亂傳
            for i in range(len(count)):
                if(count[i] > 1):
                    for j in range(video_number):
                        prob += lpSum([edge_right[j][edge[k]] for k in range(0 ,count[i])]) <= 1
                    del edge[0:count[i]]

            #out<in
            for i in range(node):
                if(count_out[i] == 1):
                    for j in range(video_number):
                        prob += lpSum([edge_right[j][node_in[k]] for k in range(0 ,count_in[i])]) >= lpSum([edge_right[j][node_out[k]] for k in range(0 ,count_out[i])])
                    del node_in[0:count_in[i]]
                    del node_out[0:count_out[i]]
                if(count_out[i] > 1):
                    for j in range(video_number):
                        for r in range(count_out[i]):
                            prob += lpSum([edge_right[j][node_in[k]] for k in range(0 ,count_in[i])]) >= lpSum(edge_right[j][node_out[r]])
                    del node_in[0:count_in[i]]
                    del node_out[0:count_out[i]]


            #print(prob)


            start = time.perf_counter()
            prob.solve()
            runtime = time.perf_counter() - start
            #the state of the solution
            print("Status:", LpStatus[prob.status])
            #print out the solution and object value
            print('The soluition  =',value(prob.objective))
            '''
            for i in prob.variables():
                print(i.name,'=',i.varValue)
            '''
            t.append(runtime)
        t_avg.append(sum(t)/len(t))
print(t_avg)
