# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 17:21:56 2024

Jochen L. Cremer
Related publication: https://arxiv.org/abs/2505.19551 
Cite: Cremer, Jochen L. "Customising Electricity Contracts at Scale with Large Language Models." arXiv preprint arXiv:2505.19551 (2025).


"""
import cvxpy as cp
import pandas as pd
import numpy as np
import time
    
def create_scopf(data,lcontingencies): 
    #PREPARE OPTIMIZATION PROBLEM
    #Variables and parameter declarations
    ngen = len(data['gen'])
    nload = len(data['load'])
    nbus = len(data['bus'])
    nline = len(data['line'])
    Sbase = data['par']['base'][0]
    
    nconti = len(lcontingencies)
    
    b_a = np.arange(nbus)
    #b_a = np.delete(b_a,data['par']['refnode'][0])
    
    Pd = cp.Parameter(nload)
    cg = cp.Parameter(ngen)
    Gonline = cp.Parameter(ngen)
    Pg = cp.Variable(ngen)
    Fl = cp.Variable(nline)
    Th = cp.Variable(nbus)
    
    
    Flc = cp.Variable((nline,nconti))
    Thc = cp.Variable((nbus,nconti))
    lam1 = cp.Variable(nbus)
    lam2 = cp.Variable(nbus)
    lam1c = cp.Variable((nbus,nconti))
    lam2c = cp.Variable((nbus,nconti))
    
    minfl = np.array(-data['line']['max_f']/Sbase)
    maxfl = np.array(data['line']['max_f']/Sbase)   
    ming = np.array(-data['gen']['max_p']/Sbase)
    maxg = np.array(-data['gen']['min_p']/Sbase)
    
    #Pd.value =  np.array(data['load']['p'])/Sbase
    #cg.value = np.array(data['gen']['cost'])
    
    #Constraints
    constraints = [ lam1 >= 0.0, lam2 >=0.0, lam1c >= 0.0, lam2c >=0.0]
    for g in range(ngen):
        constraints += [ Pg[g] >= ming[g]*Gonline[g], Pg[g] <= maxg[g]*Gonline[g]]
        
    constraints += [ Fl >= minfl, Fl <= maxfl ]
    constraints += [Th[data['par']['refnode'][0]] == data['par']['va_degree'][0]]
    
    constraints += [ Flc >= np.tile((-data['line']['max_f']/Sbase),(nconti,1)).transpose() , Flc <= np.tile(data['line']['max_f']/Sbase,(nconti,1)).transpose() ]
    constraints += [Thc[data['par']['refnode'][0],:] == data['par']['va_degree'][0]]
    
    #constraint for node balances
    for b in range(nbus):
        constraints += [ - sum(Pd[k1] for k1 in range(nload) if int( data['load']['bus'][k1]) == b ) + sum(Pg[k2] for k2 in range(ngen) if int(data['gen']['bus'][k2]) == b )
                        == lam1[b] - lam2[b] + sum(Fl[l1] for l1 in range(nline) if int( data['line']['to_bus'][l1]) == b )  - sum(Fl[l2] for l2 in range(nline) if int(data['line']['from_bus'][l2]) == b ) ]
    

    for c in range(nconti):
        for b in range(nbus):
            constraints += [ - sum(Pd[k1] for k1 in range(nload) if int( data['load']['bus'][k1]) == b ) + sum(Pg[k2] for k2 in range(ngen) if int(data['gen']['bus'][k2])==b) 
                            == lam1c[b,c] - lam2c[b,c] + sum(Flc[l1,c] for l1 in range(nline) if ( int( data['line']['to_bus'][l1]) == b and l1 != lcontingencies[c]) )  - sum(Flc[l2,c] for l2 in range(nline) if (int(data['line']['from_bus'][l2])==b and l2 != lcontingencies[c])) ]   

    
    #constraint for line flows
    for l in range (nline):
        constraints += [ Fl[l] == Sbase/data['line']['x'][l] *(sum(Th[k1] for k1 in range(nbus) if int(data['line']['from_bus'][l])==b_a[k1]) - sum(Th[k2] for k2 in range(nbus) if int(data['line']['to_bus'][l])==b_a[k2])) ]
    
    for c in range(nconti):
        for l in range (nline):
            if l!=lcontingencies[c]: 
                constraints += [ Flc[l,c] == Sbase/data['line']['x'][l] *(sum(Thc[k1,c] for k1 in range(nbus) if int(data['line']['from_bus'][l])==b_a[k1]) - sum(Thc[k2,c] for k2 in range(nbus) if int(data['line']['to_bus'][l])==b_a[k2])) ]

        
    
    objective = cp.Minimize( cp.sum( cp.multiply(cg,Pg)) + 1000000* cp.sum(lam1) + 999999* cp.sum(lam2) + 1000* cp.sum(lam1c) + 999* cp.sum(lam2c))
                    
    problem= cp.Problem(objective, constraints)
    
    return problem, Pd, cg, Pg, Fl, Th, Flc, Gonline, lam1, lam2, lam1c, lam2c

def planner(startweek, duration, generatorassetnumber):    
    #startweek = 10 #a number between 1 and 50
    #duration = 4 #in weeks: a number between 1 and 10
    #generator = 0 #a number between 1 and 19

    start = time.time()
    
 
    np.random.seed(0)
    
    planninghorizon = 356
    defaultmaintenace = 7*4
    ratio_scheduled = 0.5
    N_1 = 10
    loadlevel = 0.5
    data = pd.read_excel('IEEE118New.xlsx',sheet_name=None)
    windload = pd.read_excel('IEEE118_Load_Wind2.xlsx',sheet_name=0)[0:planninghorizon]    
    Sbase = data['par']['base'][0]
    #windload = pd.read_csv('IEEE118_Load_Wind2.csv', header=None)
    #listcontis = [0]#range(len(data['line']))
    listcontis = np.random.choice(range(0,len(data['line'])),N_1,replace=False) #[28,  51,  45, 143,  59] #n
    
    scheduledgenerators = np.random.choice(range(0,len(data['gen'])),int(ratio_scheduled*len(data['gen'])),replace=False)
    startdays = np.random.randint(0,planninghorizon,int(ratio_scheduled*len(data['gen'])))
    
    online_gens = np.ones((planninghorizon,len(data['gen'])),dtype=bool)
    
    problem, Pd, cg, Pg, Fl, Th, Flc, Gonline, lam1, lam2, lam1c, lam2c= create_scopf(data,lcontingencies = listcontis)
    cg.value = np.array(data['gen']['cost'])
    
    for i in range(len(scheduledgenerators)):
        schg = scheduledgenerators[i]
        for d in range(startdays[i],startdays[i]+defaultmaintenace+1):
            if d<=planninghorizon-1: online_gens[d,schg] = 0
            
    #process user request
    online_gens[:,generatorassetnumber] = 0
    possiblemaintenance = np.ones(planninghorizon)
    conti_matrix = np.zeros((len(data['bus']),N_1))   
     
    #scenario = np.random.randint(len(windload))
    for scenario in range(len(windload)): 
        Pd.value = loadlevel*np.array(windload.iloc[scenario])/Sbase 
        #for go in range(len(data['gen'])): data['gen'].loc[go,'in_service'] = online_gens[scenario,go]         
        Gonline.value = np.array((online_gens[scenario,:]),int)
        
        solution  = problem.solve(solver=cp.GUROBI)
        secure = np.all([np.all(np.abs(lam1.value)==0),np.all(np.abs(lam2.value)==0),np.all(np.abs(lam1c.value)==0),np.all(np.abs(lam2c.value)==0)])
        #print(secure)
        possiblemaintenance[scenario] = secure
        
        
        
        if scenario >= startweek*7 and scenario <= startweek*7+duration*7:
            contis1 =np.array(lam1c.value)
            contis2 =np.array(lam2c.value)
            conti_matrix = conti_matrix + contis1+contis2
            contis = listcontis[np.where(np.sum(conti_matrix,0)>0)]            
            df2 = pd.DataFrame(contis)

            
        
    possiblestartdays = np.zeros(planninghorizon)
    for scenario in range(len(windload)):
        possiblestartdays[scenario] = np.all(possiblemaintenance[scenario:(scenario+duration*7)])
        
    if possiblestartdays[startweek*7]==1:
        statement = "Yes, it is possible to disconnect at your requested time. "
    else:
        statement = "We know you wanted to disconnect your generator for " + str(duration) + " weeks starting at week " + str(startweek) + ", so at day" + str(startweek*7)+". This is unfortunately not possible."
        Startdateearlier = -1
        Earlieststartdateearlier = -1 
        for i in range(startweek*7, 0, -1):        
            if possiblestartdays[i]==1: 
                Startdateearlier = i
                Earlieststartdateearlier = i
                for k in range(i,0,-1):
                    if possiblestartdays[k]==0 or k ==1:
                        Earlieststartdateearlier = k
                        break            
                statement = statement + "You could disconnect earlier. If you want to connect earlier, you could disconnect your generator for the duration of " + str(duration) + " weeks starting at any day between day " + str(Earlieststartdateearlier) + " and day " + str(Startdateearlier) + "." 
                break
            
        
        Startdateafterwards = -1
        Lateststartdateafterwards = -1    
        for i in range(startweek*7,planninghorizon):
            if possiblestartdays[i]==1: 
                Startdateafterwards = i
                Lateststartdateafterwards = i
                for k in range(i,planninghorizon):
                    if possiblestartdays[k]==0 or k==planninghorizon-1:
                        Lateststartdateafterwards = k-1
                        break
                statement = statement + "You could disconnect later. If you want to connect later, you could disconnect your generator for the duration of " + str(duration) + " weeks starting at any day between day " + str(Startdateafterwards) + " and day " + str(Lateststartdateafterwards)+ "."
                break     
    end = time.time()
    print(end - start)
    
    df1 = pd.DataFrame(online_gens)
    df3 = pd.DataFrame(possiblemaintenance)
    df4 = pd.DataFrame(possiblestartdays)
    df5 = pd.DataFrame(startdays)


    with pd.ExcelWriter('output.xlsx') as writer:  # doctest: +SKIP
        df1.to_excel(writer, sheet_name='online_gens')
        df2.to_excel(writer, sheet_name='contis')
        df3.to_excel(writer, sheet_name='possiblemaintenance')
        df4.to_excel(writer, sheet_name='possiblestartdays')
        df5.to_excel(writer, sheet_name='startdays')
        
 
    return statement
    
    
