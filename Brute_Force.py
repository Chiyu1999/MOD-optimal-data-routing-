
import pulp
import numpy as np
from collections import OrderedDict
import time
import random

t_avg=[]
branch_avg=[]
for n in range(12,14,2):
    t=[]
    b_avg=[]
    for times in range(1):
        video_num = 3
        node_num = n # not include the server node

        input_number = [0 for i in range(node_num)]

        for i in range(len(input_number)):
            input_number[i] = random.randint(1,i+1) # ex:第3個節點的進入點可能有1~3個

        link_s = []
        link_d = []
        upstreamm = []
        for i in range(len(input_number)):
            upstreamm.append(np.random.choice(range(i+1), input_number[i], False)) # 分別決定每個節點(不包括server)有哪些上游節點

        for i in range(node_num):
            for j in range(len(upstreamm)):
                upstreamm[j] = list(upstreamm[j])
                if upstreamm[j].count(i) > 0:
                    link_s.append(i)
                    link_d.append(j+1)
                else:
                    continue

        demand_for_bb = [[0 for j in range(video_num)] for i in range(node_num)]
        for i in range(node_num):
            for j in range(video_num):
                demand_for_bb[i][j] = random.randint(0,20)

        bandwidth = [0 for _ in range(len(link_d))]
        for i in range(len(link_d)):
            bandwidth[i] = random.randint(1, video_num-1)

        bandwidth_for_bb = [0 for i in range(node_num)]
        for i in range(1,node_num+1):
            rr=0
            for j in range(len(link_d)):
                if link_d[j]==i:
                    rr=rr+bandwidth[j]
            bandwidth_for_bb[i-1]=rr

        all_upper_bound_list=[ [] for k in range(node_num)]
        all_temp_obj=[ [] for k in range(node_num)]
        all_branch = [ [] for k in range(node_num)]#
        all_count=[[] for k in range(node_num)]#
        index_current=[0 for i in range(node_num)]
        index_opt=[0 for i in range(node_num)]
        best_path=[]
        temp_opt=0
        temp_i = 0
        temp_branch_upstream = [[0 for i in range(video_num)] for j in range(node_num)]
        count=0
        opt_count = 0 
        total_branch = 0

        ##上游列表##
        count_in = [0 for _ in range(node_num)]
        node_in = []
        #紀錄每個節點有幾條路徑進入
        for i in range(1,node_num+1): 
            for j in range(len(link_d)):
                if(link_d[j] == i):
                    count_in[i-1] += 1
        #紀錄每個節點進入的前一個節點
        for i in range(1,node_num+1):
            for j in range(len(link_d)):
                if(link_d[j] == i):
                    node_in.append(link_s[j])


        def find_branch_and_its_upper_bound(i):
            global count
            global temp_opt
            global index_opt
            global temp_i
            global opt_count
            branch_list = []
            x1 = [0 for i in range(video_num)]
            profit_temp = [0 for i in range(node_num)]
            a=0
            b=0
            c=0
            temp_node = []
            for k in range(len(node_in)):
                temp_node.append(node_in[k])
            num_upstream=0
            upper_bound_list=[]
            temp_obj=[]
            video_temp = []
            count_bandwidth=[0 for i in range(node_num + 1)]
            branch_1 = [[1,0,0],[0,1,0],[0,0,1]]
            branch_2 = [[1,1,0],[1,0,1],[0,1,1]]

            if(i == node_num-1):
                flag = 0
                num_upstream = 0
                o = 0
                for k in range(i):  #把當前節點的上游節點從0開始排
                    num_upstream += count_in[k]
                del temp_node[0:num_upstream]   

                #把上游節點所對應的頻寬列成count_bandwidth、video_temp為當前節點能提供的影片
                for k in range(0,count_in[i]): 
                    if(temp_node[k]==0):
                        video_temp.append([1,1,1])
                        for j in range(len(link_d)):
                            if((link_d[j] == i+1) & (link_s[j] == 0)):
                                count_bandwidth[0]=bandwidth[j]
                    else:
                        video_temp.append(temp_branch_upstream[temp_node[o]-1])
                        o+=1
                        for j in range(len(link_d)):
                            if((link_d[j] == i+1) & (link_s[j] == temp_node[k])):
                                count_bandwidth[temp_node[k]] = bandwidth[j]

                #判斷分支方法；列出可行分支 
                all_possible_branch = [[] for k in range(node_num+1)]
                for k in range(0,count_in[i]):
                    temp_branch = []
                    if(sum(video_temp[k]) > count_bandwidth[temp_node[k]]): #需要去分解上游並設定可以收到的相應影片的分支
                        flag = 1
                        if(count_bandwidth[temp_node[k]]==1): #b=1  
                            for j in range(3):
                                count_pos = 0
                                for z in range(3):
                                    if((video_temp[k][z]-branch_1[j][z]) >= 0):
                                        count_pos += 1
                                if(count_pos == 3):
                                    temp_branch.append(branch_1[j])
                    
                        elif(count_bandwidth[temp_node[k]]==2):#b=2
                            for j in range(3):
                                count_pos = 0
                                for z in range(3):
                                    if((video_temp[k][z]-branch_2[j][z]) >= 0):
                                        count_pos += 1
                                if(count_pos == 3):
                                    temp_branch.append(branch_2[j])   
                        all_possible_branch[temp_node[k]] = temp_branch            
                    else:
                        all_possible_branch[temp_node[k]].append(video_temp[k])
        
                if(flag == 1): 
                    temp_branch_sum = []
                    temp_list = []
                    for k in range(count_in[i]-1): #分解後相加 總共累加幾次
                        for j in range(len(all_possible_branch[temp_node[k+1]])):
                            temp_list = np.add(all_possible_branch[temp_node[k]],all_possible_branch[temp_node[k+1]][j])
                            for z in range(len(temp_list)):
                                temp_branch_sum.append(temp_list[z])              
                       
                    for k in range(len(temp_branch_sum)):#相加後有大於1要變成1
                        for j in range(3):
                            if(temp_branch_sum[k][j] > 1):
                                temp_branch_sum[k][j] = 1
                    #把重複的刪掉
                    temp_branch_nosame = []  
                    temp_branch_nosame = list(set([tuple(t)for t in temp_branch_sum]))
                    for k in range(len(temp_branch_nosame)):
                        branch_list.append(list(temp_branch_nosame[k]))
                    if(len(branch_list)==0):
                        for k in range(len(temp_node)):
                            for t in range(len(all_possible_branch[temp_node[k]])):
                                branch_list.append(all_possible_branch[temp_node[k]][t])
        
                if(flag == 0): #所有的上游節點的bandwidth>= num_video_provided 直接傳送可行的影片
                    g = [0,0,0]
                    for k in range(video_num):
                        for j in range(len(video_temp)):
                             g[k] +=video_temp[j][k]

                    for k in range(len(g)):
                        if(g[k] > 1):
                            g[k] = 1    
                    branch_list.append(g)
        
                count=len(branch_list)
                #確定後找節點能獲得的profit
                temp=[]
                for z in range(len(branch_list)):
                    temp.append(pulp.lpSum([demand_for_bb[i][j]*branch_list[z][j] for j in range(video_num)])) #第i個節點獲得的profit

                for z in range(len(branch_list)):
                    objj=0
                    objj+=all_temp_obj[i-1][index_current[i-1]]          
                    temp_obj.append(int(pulp.value(temp[z]))+objj)

                for k in range(len(branch_list)):
                    all_branch[i].append(branch_list[k])       
                for k in range(len(branch_list)):
                    all_temp_obj[i].append(temp_obj[k])
        
        
                for k in range(len(temp_obj)):           
                    if (temp_obj[k]>temp_opt):                
                        temp_opt = temp_obj[k]
                        index_current[i] = opt_count
                        for y in range(len(index_current)):
                            index_opt[y]=index_current[y]
                    opt_count+=1

            elif(i==0):
                for a in range(2):
                    for b in range(2):
                        for c in range(2):
                            if (a+b+c == bandwidth_for_bb[i]):
                                g=[a,b,c] #(a,b,c)分支
                                branch_list.append(g)

                                temp_for_begin = pulp.lpSum([demand_for_bb[i][j]*g[j] for j in range(video_num)]) #第i個節點獲得的profit

                                #計算後面節點的upper bound
                                for i1 in range(i+1,node_num):#每個節點解一次貪婪最佳化####
                                    model = pulp.LpProblem("value max", pulp.LpMaximize)
                                    for v in range(video_num):
                                        x1[v] = pulp.LpVariable("x1  video%d"%(v), lowBound=0, cat='Binary')
                                    model += pulp.lpSum([demand_for_bb[i1][j]*x1[j] for j in range(video_num)])
                                    model += pulp.lpSum([x1[j] for j in range(video_num)]) <= bandwidth_for_bb[i1]
                                    model.solve()
                                    profit_temp[i1] = pulp.value(model.objective)

                                upper_bound = sum(profit_temp)+int(pulp.value(temp_for_begin))#(a,b,c)分支的upper bound
                                upper_bound_list.append(upper_bound)
                                temp_obj.append(int(pulp.value(temp_for_begin)))
                                profit_temp = [0 for i in range(node_num)]#歸零

                count=len(branch_list)
                for k in range(len(branch_list)):
                    all_branch[i].append(branch_list[k])
                for k in range(len(upper_bound_list)):
                    all_upper_bound_list[i].append(upper_bound_list[k])
                for k in range(len(branch_list)):
                    all_temp_obj[i].append(temp_obj[k])

       
        
                for k in range(len(temp_obj)):
                    if (temp_obj[k]>temp_opt):
                        temp_opt=temp_obj[k]

    
            else:
                flag = 0
                num_upstream = 0
                o = 0
                for k in range(i):  #把當前節點的上游節點從0開始排
                    num_upstream += count_in[k]
                del temp_node[0:num_upstream]   

                #把上游節點所對應的頻寬列成count_bandwidth、video_temp為當前節點能提供的影片
                for k in range(0,count_in[i]): 
                    if(temp_node[k]==0):
                        video_temp.append([1,1,1])
                        for j in range(len(link_d)):
                            if((link_d[j] == i+1) & (link_s[j] == 0)):
                                count_bandwidth[0]=bandwidth[j]
                    else:                
                        video_temp.append(temp_branch_upstream[temp_node[k]-1])
                        #o+=1
                        for j in range(len(link_d)):
                            if((link_d[j] == i+1) & (link_s[j] == temp_node[k])):
                                count_bandwidth[temp_node[k]] = bandwidth[j]
  
                all_possible_branch = [[] for k in range(node_num +1)] #
                for k in range(0,count_in[i]):
                    temp_branch = []
                    if(sum(video_temp[k]) > count_bandwidth[temp_node[k]]): #需要去分解上游並設定可以收到的相應影片的分支
                        flag = 1
                        if(count_bandwidth[temp_node[k]]==1): #b=1  
                            for j in range(3):
                                count_pos = 0
                                for z in range(3):
                                    if((video_temp[k][z]-branch_1[j][z]) >= 0):
                                        count_pos += 1
                                if(count_pos == 3):
                                    temp_branch.append(branch_1[j])
                    
                        elif(count_bandwidth[temp_node[k]]==2):#b=2
                            for j in range(3):
                                count_pos = 0
                                for z in range(3):
                                    if((video_temp[k][z]-branch_2[j][z]) >= 0):
                                        count_pos += 1
                                if(count_pos == 3):
                                    temp_branch.append(branch_2[j])   
                        all_possible_branch[temp_node[k]] = temp_branch            
                    else:
                        all_possible_branch[temp_node[k]].append(video_temp[k])

        
                if(flag == 1): 
                    temp_branch_sum = []
                    temp_list = []
                    for k in range(count_in[i]-1): #分解後相加 總共累加幾次
                        for j in range(len(all_possible_branch[temp_node[k+1]])):
                            temp_list = np.add(all_possible_branch[temp_node[k]],all_possible_branch[temp_node[k+1]][j])
                            for z in range(len(temp_list)):
                                temp_branch_sum.append(temp_list[z])              
            
            
                    for k in range(len(temp_branch_sum)):#相加後有大於1要變成1
                        for j in range(3):
                            if(temp_branch_sum[k][j] > 1):
                                temp_branch_sum[k][j] = 1
                    #把重複的刪掉
                    temp_branch_nosame = []  
                    temp_branch_nosame = list(set([tuple(t)for t in temp_branch_sum]))
                    for k in range(len(temp_branch_nosame)):
                        branch_list.append(list(temp_branch_nosame[k]))
                    if(len(branch_list)==0):
                        for k in range(len(temp_node)):
                            for t in range(len(all_possible_branch[temp_node[k]])):
                                branch_list.append(all_possible_branch[temp_node[k]][t])
        
                if(flag == 0): #所有的上游節點的bandwidth>= num_video_provided 直接傳送可行的影片
                    g = [0,0,0]
                    for k in range(video_num):
                        for j in range(len(video_temp)):
                             g[k] +=video_temp[j][k]

                    for k in range(len(g)):
                        if(g[k] > 1):
                            g[k] = 1    
                    branch_list.append(g)
        
                count=len(branch_list)
                #確定後找節點能獲得的profit
                temp=[]
                for z in range(len(branch_list)):
                    temp.append(pulp.lpSum([demand_for_bb[i][j]*branch_list[z][j] for j in range(video_num)])) #第i個節點獲得的profit

                profit_temp = [0 for i in range(node_num)]#歸零
                #計算後面節點的upper bound
                for i1 in range(i+1,node_num):#每個節點解一次貪婪最佳化#####
                    model = pulp.LpProblem("value max", pulp.LpMaximize)
                    for v in range(video_num):
                        x1[v] = pulp.LpVariable("x1  video%d"%(v), lowBound=0, cat='Binary')
                    model += pulp.lpSum([demand_for_bb[i1][j]*x1[j] for j in range(video_num)])
                    model += pulp.lpSum([x1[j] for j in range(video_num)]) <= bandwidth_for_bb[i1]
                    model.solve()
                    profit_temp[i1] = pulp.value(model.objective)

                for z in range(len(branch_list)):
                    objj=0
                    objj+=all_temp_obj[i-1][index_current[i-1]]
                    upper_bound = sum(profit_temp)+int(pulp.value(temp[z]))+objj#(a,b,c)分支的upper bound
                    upper_bound_list.append(upper_bound)
                    temp_obj.append(int(pulp.value(temp[z]))+objj)

                for k in range(len(branch_list)):
                    all_branch[i].append(branch_list[k])
                for k in range(len(upper_bound_list)):
                    all_upper_bound_list[i].append(upper_bound_list[k])
                for k in range(len(branch_list)):
                    all_temp_obj[i].append(temp_obj[k])
       
                for k in range(len(temp_obj)):           
                    if (temp_obj[k]>temp_opt):                
                        temp_opt = temp_obj[k]
                        index_current[i] = opt_count
                        for y in range(len(index_current)):
                            index_opt[y]=index_current[y]
                    opt_count+=1

        opt_flag = 0 #結束
        i=0 #起始
        start = time.perf_counter()
        find_branch_and_its_upper_bound(i)
        for k in range(count):
            all_count[i].append(1)

        total_branch += sum(all_count[i])

        while(opt_flag==0):
            upper_bound_list=[]
            temp_obj=[]
            temp_video =[]
    
            if(i==0):
                for j in range(sum(all_count[i])):
                    if (all_upper_bound_list[i][j]>temp_opt):               
                        temp_branch_upstream[i] = all_branch[i][j] #當前節點所能提供的影片
                        index_current[i]=j 
                        find_branch_and_its_upper_bound(i+1)
                        all_count[i+1].append(count) #上一層的每條分支分別的分支數量
                    else:
                        all_count[i+1].append(0)       
                if(node_num <= 2):
                    opt_flag = 1

            elif(i == node_num-2):
                count_num = [ 0 for k in range(node_num)]    #計數上游改變的次數 
                temp_count = [ 0 for k in range(node_num)]   #計數上上游改變的位置
                index_current = [ 0 for k in range(node_num)]#目前位置
                change_count = [ 0 for k in range(node_num)] #計數累加
                temp_j = 0
                opt_count = 0
                for k in range(i+1):
                    change_count[k] = all_count[k][0]

                for j in range(len(all_count[i])):
                    for v in range(all_count[i][j]):
                        index_current[i] = temp_j #上游
                        temp_count[i] = temp_j
                        temp_branch_upstream[i] = all_branch[i][temp_j] #上游目前提供影片
                        for k in range(i-1,-1,-1):                                                                    
                            if(index_current[k+1] >= change_count[k+1]): 
                                count_num[k+1] = count_num[k+1] + 1
                                change_count[k+1] += all_count[k+1][count_num[k+1]]
                                temp_count[k] = (temp_count[k] + 1)
                                index_current[k] = temp_count[k] 
                                temp_branch_upstream[k] = all_branch[k][temp_count[k]] #上上游目前提供影片
                            else:                       
                                index_current[k]=temp_count[k]
                                temp_branch_upstream[k] = all_branch[k][index_current[k]]
                        find_branch_and_its_upper_bound(i+1)
                        all_count[i+1].append(count)#上一層的每條分支分別的分支數量              
                        temp_j+=1    
                opt_flag=1
                total = time.perf_counter() - start

            else:
                count_num = [ 0 for k in range(node_num)]    #計數上游改變的次數 
                temp_count = [ 0 for k in range(node_num)]   #計數上上游改變的位置
                index_current = [ 0 for k in range(node_num)]#目前位置
                change_count = [ 0 for k in range(node_num)] #計數累加
                temp_j = 0
                opt_count = 0
                for k in range(i+1):
                    change_count[k] = all_count[k][0]

                for j in range(len(all_count[i])):
                    for v in range(all_count[i][j]):
                        index_current[i] = temp_j #上游
                        temp_count[i] = temp_j
                        temp_branch_upstream[i] = all_branch[i][temp_j] #上游目前提供影片
                        for k in range(i-1,-1,-1):                                                                    
                            if(index_current[k+1] >= change_count[k+1]): 
                                count_num[k+1] = count_num[k+1] + 1
                                change_count[k+1] += all_count[k+1][count_num[k+1]]
                                temp_count[k] = (temp_count[k] + 1)
                                index_current[k] = temp_count[k] 
                                temp_branch_upstream[k] = all_branch[k][temp_count[k]] #上上游目前提供影片
                            else:                       
                                index_current[k]=temp_count[k]
                                temp_branch_upstream[k] = all_branch[k][index_current[k]]
                        find_branch_and_its_upper_bound(i+1)
                        all_count[i+1].append(count)#上一層的每條分支分別的分支數量              
                        temp_j+=1                
            i+=1


        for k in range(len(all_count)):
            total_branch += sum(all_count[i])
        print("總分支數量:",total_branch)
        print("最佳提供用戶數量:",temp_opt)
        print("Total time:", total)
        for i in range(len(all_branch)):
            best_path.append(all_branch[i][index_opt[i]])
        print("最佳路徑為:",best_path)   
        b_avg.append(total_branch)
        t.append(total)
    branch_avg.append(sum(b_avg)/len(b_avg))
    t_avg.append(sum(t)/len(t))
print(t_avg)
print(branch_avg)

