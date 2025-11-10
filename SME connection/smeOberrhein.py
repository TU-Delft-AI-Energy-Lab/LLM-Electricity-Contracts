# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 13:54:53 2025

Jochen L. Cremer
Related publication: https://arxiv.org/abs/2505.19551 
Cite: Cremer, Jochen L. "Customising Electricity Contracts at Scale with Large Language Models." arXiv preprint arXiv:2505.19551 (2025).

"""

import numpy as np
import pandas as pd

from pandapower.control import ConstControl
from pandapower.networks import mv_oberrhein
from pandapower.timeseries import run_timeseries, OutputWriter
from pandapower.timeseries.data_sources.frame_data import DFData
from pandapower.plotting.plotly import pf_res_plotly
import pandapower as pp
import pandapower.networks
import pandapower.contingency
import pandapower.control
import pandapower.timeseries
import pandapower.plotting
import pandapower.control as control
from matplotlib import pyplot as plt
import tikzplotlib
import webcolors
from matplotlib import rc
from matplotlib.lines import Line2D
from matplotlib.legend import Legend
import random




#Parameters
volt_limits = [0.975,1.03]
power_limit = [0,60]
n_ts = 24 # number of time steps
working_location = 'SME connection'



rc('text', usetex=True)
rc('font', **{'family': 'serif', 'serif': ['cmr10']})
rc('axes.formatter', use_mathtext=True)


def closest_colour(requested_colour):
    min_colours = {}
    for name in webcolors.names("css3"):
        r_c, g_c, b_c = webcolors.name_to_rgb(name)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


Line2D._us_dashSeq    = property(lambda self: self._dash_pattern[1])
Line2D._us_dashOffset = property(lambda self: self._dash_pattern[0])
Legend._ncol = property(lambda self: self._ncols)



def create_plots(load_profiles, ow):
    #plot results
    fig, (ax1, ax2, ax3) = plt.subplots(ncols=1, nrows=3, figsize=(8,12))
    
    ax1.plot(np.array(range(n_ts)),load_profiles.mean(axis=1),label="Load level (power)", linestyle="-", color='tab:orange')
    ax1.set_ylabel("Mean load (MW)")
    ax1.set_xlabel("Time step")
    #ax1.legend(ncol=2, loc="upper center", bbox_to_anchor=[0.5, -0.3])
    
    
    plt.rcParams['font.family'] = 'DeJavu Serif'
    plt.rcParams['font.serif'] = ['Times New Roman']
    
    plt.rcParams.update({
    "font.family": "serif",
    # Use LaTeX default serif font.
    "font.serif": [],
    # Use specific cursive fonts.
    "font.cursive": ["Comic Neue", "Comic Sans MS"],
    })
    
    ow.output["res_line.loading_percent"].min(axis=1).plot(label="min. Loading (\%)", ax=ax2)
    ow.output["res_line.loading_percent"].max(axis=1).plot(label="max. Loading (\%)", ax=ax2)
    
    ax2.plot(np.array(range(n_ts)), np.repeat(power_limit[1],n_ts),label="upper limit Loading (\%)", linestyle="--", color='tab:orange')
    
    ax2.legend(ncol=2, loc="upper center", bbox_to_anchor=[0.35, 0.9])
    ax2.set_ylabel("Line loading (\%)")
    ax2.set_xlabel("Time step")
    
    #ow.output["res_bus.max_vm_pu"].max(axis=1).plot(label="max. $V_m$, N-1 (p.u.)", ax=ax2, linestyle="--")
    ow.output["res_bus.vm_pu"].min(axis=1).plot(label="min. $V_m$ (p.u.)", ax=ax3)
    ow.output["res_bus.vm_pu"].max(axis=1).plot(label="max. $V_m$ (p.u.)", ax=ax3)
    #ow.output["res_bus.min_vm_pu"].min(axis=1).plot(label="min. $V_m$, N-1 (p.u.)", ax=ax2, linestyle="--")    
    
    
    ax3.plot(np.array(range(n_ts)), np.repeat(volt_limits[0],n_ts),label="lower limit $V_m$ (p.u.)", linestyle="--",color='tab:blue')
    ax3.plot(np.array(range(n_ts)), np.repeat(volt_limits[1],n_ts),label="upper limit $V_m$ (p.u.)", linestyle="--",color='tab:orange')
    ax3.legend(ncol=2, loc="upper center", bbox_to_anchor=[0.35, 0.9])
    ax3.set_ylabel("Bus voltage magnitude (p.u.)")
    ax3.set_xlabel("Time step")

    
    
    fig.savefig(working_location+"\\figures\\pfoberrhein.pdf", bbox_inches='tight')
    
    tikzplotlib.save(working_location+"\\figures\\pfoberrhein.tex",encoding='utf-8')
    
    
    
    return fig




def planner(zipcode, load1h, load2h, load3h, load4h, load5h, load6h, load7h, load8h, load9h, load10h, load11h, load12h, load13h, load14h, load15h, load16h, load17h, load18h, load19h, load20h, load21h, load22h, load23h, load24h, details =0):
    
    net = mv_oberrhein(scenario='generation')

    pd.set_option('future.no_silent_downcasting', True)
    # load your timeseries from a file (here csv file)
    # df = pd.read_csv("sgen_timeseries.csv")
    # or create a DataFrame with some random time series as an example
   # or create a DataFrame with some random time series as an example
   
    base_load_factor = 1.12
    time_profile = base_load_factor + 0.7* np.array([0.209279, 0.154806, 0.141973, 0.138203, 0.140447, 0.168267, 0.323342, 0.464507, 0.479225, 0.442251, 0.417213, 0.424751, 0.469174, 0.464776, 0.414072, 0.37629, 0.377726, 0.461815, 0.59652, 0.67145, 0.60388, 0.50606, 0.41883, 0.31015])
       
    load_profiles = pd.DataFrame(net.load.p_mw.values*(np.transpose(np.tile(time_profile,(len(net.load),1)))), 
                                 index=np.arange(24), columns=net.load.index.values)
    
    load_profiles[zipcode] = load_profiles[zipcode] + np.array( [load1h, load2h, load3h, load4h, load5h, load6h, load7h, load8h, load9h, load10h, load11h, load12h, load13h, load14h, load15h, load16h, load17h, load18h, load19h, load20h, load21h, load22h, load23h, load24h])
   
    dsl = pp.timeseries.DFData(load_profiles)
    const_load = pp.control.ConstControl(net, element="load", variable="p_mw", element_index=net.load.index.values, 
                            profile_name=net.load.index.values, data_source=dsl)
    
    
    gen_profiles = pd.DataFrame(net.sgen.p_mw.values * np.transpose(np.tile(time_profile,(len(net.sgen),1))), 
                                 index=np.arange(24), columns=net.sgen.index.values)
    dsg = pp.timeseries.DFData(gen_profiles)
    const_sgen = pp.control.ConstControl(net, element="sgen", variable="p_mw", element_index=net.sgen.index.values, 
                            profile_name=net.sgen.index.values, data_source=dsg)
    
    
    # initialising the outputwriter to save data to excel files in the current folder. You can change this to .json, .csv, or .pickle as well
    ow = OutputWriter(net, output_path=working_location, output_file_type=".xlsx")
    # adding vm_pu of all buses and line_loading in percent of all lines as outputs to be stored
    ow.log_variable('res_bus', 'vm_pu');
    ow.log_variable('res_line', 'loading_percent');

    
    # starting the timeseries simulation for one day
    run_timeseries(net)    
    
    # now checkout the folders res_bus and res_line in your current working dir
    
    
    df2 = pd.read_excel(working_location+'\\res_bus\\vm_pu.xlsx')
    df3 = pd.read_excel(working_location+'\\res_line\\loading_percent.xlsx')    
    
    
    powerlines = df3.to_numpy()[:,1:]
    voltages = df2.to_numpy()[:,1:]
    
    
    feasible_volt = np.all(np.concatenate((voltages>=volt_limits[0],voltages<=volt_limits[1])),axis=1)
    #https://pandapower.readthedocs.io/en/latest/networks/mv_oberrhein.html#pandapower.networks.mv_oberrhein
    feasible_power = np.all(powerlines <=power_limit[1],axis=1)
    
    feasible_per_time = np.all(voltages>=volt_limits[0],axis=1)*np.all(voltages<volt_limits[1],axis=1)*feasible_power
    
    
    #print(np.all(feasible_volt))
    #print(np.all(feasible_power))
    #counter = counter + np.all(feasible_per_time)/samples*100


    feasible = 1
    if np.all(feasible_per_time) == False:
        feasible =0
        infeasible_times = np.where(feasible_per_time==False)[0]
        
        infeasible_time = random.choice(infeasible_times)
        #print(infeasible_time+1)
       
        net["load"]["p_mw"] = load_profiles.loc[infeasible_time]
        net["sgen"]["p_mw"] = gen_profiles.loc[infeasible_time]
        pp.runpp(net)
        
        
        text = 'Times that are not possible to receive the requested power: '
        for i in range(len(infeasible_times)): 
            if i ==len(infeasible_times)-1: 
                text = text + str(infeasible_times[i]+1) + '. Please adjust your requested power profile on these times.'
            else:
                text = text + str(infeasible_times[i]+1) + ', '
    else : 
        text = 'All times are feasible to receive the requested power. We can sign an electricity contract. '
    

    create_plots(load_profiles, ow)
    
    if details == 0:
        return text
    else    :
        return(text,net,ow,feasible,load_profiles)

    

def network_analysis(samples=147):
#Note for 2MW the infeasiblezipcodes= [5, 7, 12, 19, 29, 35, 38, 39, 46, 51, 56, 59, 60, 84, 86, 87, 94, 100, 106, 107, 115]

    count = 0
    list_infeasiblebuses = [] #infeasiblezipcodes:#
    for s in range(0,samples):        
        zipcode = s#  np.random.randint(0,147)#value between [0,147]
        #2MW large consumer
    
        scale = 2
        load1h = 1*scale ; #MW
        load2h = 1*scale;
        load3h = 1*scale;
        load4h = 1*scale;
        load5h = 1*scale;
        load6h= 1*scale;
        load7h= 1*scale;
        load8h= 1*scale;
        load9h= 1*scale;
        load10h= 1*scale;
        load11h= 1*scale;
        load12h= 1*scale;
        load13h= 1*scale;
        load14h= 1*scale;
        load15h= 1*scale;
        load16h= 1*scale;
        load17h= 1*scale;
        load18h= 1*scale;
        load19h= 1*scale;
        load20h= 1*scale;
        load21h= 1*scale;
        load22h= 1*scale;
        load23h= 1*scale;
        load24h= 1*scale;
        #counter = 0
        
        output, net, ow, feasible, load_profiles = planner(zipcode, load1h, load2h, load3h, load4h, load5h, load6h, load7h, load8h, load9h, load10h, load11h, load12h, load13h, load14h, load15h, load16h, load17h, load18h, load19h, load20h, load21h, load22h, load23h, load24h, details=1)  
        count = count + feasible        
        
        if feasible ==0:
            list_infeasiblebuses.append(s)
    
        print(output)
        
    #net = mv_oberrhein(scenario='generation')
    
    #prepare network for plotting
    
    net.ext_grid.drop(index=0, inplace=True)
    net.ext_grid.drop(index=1, inplace=True)
    for i in list_infeasiblebuses: 
        pp.create_ext_grid(net, bus=net["load"]["bus"][i])    
    
    pf_res_plotly(net, climits_volt=(0.95,1.05), climits_load=(0, 100),filename='temp-plot.html')
    
    #create_plots(load_profiles, ow)
    return list_infeasiblebuses


        
    