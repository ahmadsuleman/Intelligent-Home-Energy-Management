# -*- coding: utf-8 -*-
"""
Created on Sat Jan 22 01:02:47 2022

@author: Suleman_Sahib
"""

# Import necessary modules
from Modules import appliances, EV_, EV_Schedule
import time
import numpy as np
from HEMS_Environment import home_env
import matplotlib.pyplot as plt
from MDP_Development1 import HEMS_MDP

# Initialize variables and environment
start = time.time()
home = home_env()
start_t = 0  # Start time 
end_t = 48   # End time

# Set plotting parameters
fontsize = 18  # Font size for plots
width = 20     # Graph width
height = 5     # Graph height
dpi = 100      # Image resolution, 300 or above
tick_size = 15

# Initialize lists to store data for visualization
bat1, bat2, bat3 = [], [], []  
all_t, pv, load, ev_soc = [], [], [], []
status_1, status_2, status_3, status_ev = [], [], [], []
sched = []
per_day_profit = []

# Run the simulation for 1000 steps (time units)
for i in range(1000):
    home.manage_energy(i)  # Manage the energy for the current time step
    
    # Store battery states and other data
    bat1.append(home.battries[0].soc)
    bat2.append(home.battries[1].soc)
    bat3.append(home.battries[2].soc)
    status_1.append(home.battries[0].state)
    status_2.append(home.battries[1].state)
    status_3.append(home.battries[2].state)
    status_ev.append(home.ev.state)
    all_t.append(i)
    ev_soc.append(home.ev.soc)
    pv.append(home.gen)
    load.append(home.load)
    sched.append(home.EV.at_home(i))  # EV schedule
    
    # Calculate daily profit every 24 hours (at hour 23)
    if i % 23 == 0:
        economy_time = []
        economy_profit = []
        for e, t in home.profit:
            economy_time.append(t)
            economy_profit.append(e)
        home.profit = []
        per_day_profit.append(sum(economy_profit))

# Save daily profit data
np.save("paper_results/per_day_profit_cond.npy", per_day_profit, allow_pickle=True)

# Uncommented data saving for different home system data
np.save("paper_results/Conditional_Bat_1.npy", bat1, allow_pickle=True)
np.save("paper_results/Conditional_Bat_2.npy", bat2, allow_pickle=True)
np.save("paper_results/Conditional_Bat_3.npy", bat3, allow_pickle=True)
np.save("paper_results/Conditional_status_1.npy", status_1, allow_pickle=True)
np.save("paper_results/Conditional_status_2.npy", status_2, allow_pickle=True)
np.save("paper_results/Conditional_status_3.npy", status_3, allow_pickle=True)
np.save("paper_results/Conditional_status_ev.npy", status_ev, allow_pickle=True)
np.save("paper_results/Conditional_ev_soc.npy", ev_soc, allow_pickle=True)
np.save("paper_results/Conditional_PV.npy", pv, allow_pickle=True)
np.save("paper_results/Conditional_Load.npy", load, allow_pickle=True)
np.save("paper_results/Conditional_EV_Schedule.npy", sched, allow_pickle=True)

# Save energy data for import/export and grid costs
time_steps1, grid_cost = [], []
for e, t in home.profit:
    time_steps1.append(t)
    grid_cost.append(e)
np.save("paper_results/Conditional_Export_Profit.npy", grid_cost, allow_pickle=True)
np.save("paper_results/Conditional_export_profit_time.npy", time_steps1, allow_pickle=True)

# Save grid import costs
time_steps1, grid_cost = [], []
for e, t in home.grid_cost:
    time_steps1.append(t)
    grid_cost.append(e)
np.save("paper_results/Conditional_import_cost.npy", grid_cost, allow_pickle=True)
np.save("paper_results/Conditional_import_cost_time.npy", time_steps1, allow_pickle=True)

# Save energy data for imported and saved energy
tstep2, energy2 = [], []
for e, t in home.imported_from_grid:
    tstep2.append(t)
    energy2.append(e)
np.save("paper_results/Conditional_Imported_from_Grid.npy", energy2, allow_pickle=True)
np.save("paper_results/Conditional_import_time.npy", tstep2, allow_pickle=True)

tstep1, energy1 = [], []
for e, t in home.saved_in_batteries:
    tstep1.append(t)
    energy1.append(e)
np.save("paper_results/Conditional_Save_In_Bat.npy", energy1, allow_pickle=True)
np.save("paper_results/Conditional_Sabe_Bat_time.npy", tstep1, allow_pickle=True)

tstep, energy = [], []
for e, t in home.used_from_batteries:
    tstep.append(t)
    energy.append(e)
np.save("paper_results/Conditional_Used_from_Bat.npy", energy, allow_pickle=True)
np.save("paper_results/Conditional_Time_Bat_use.npy", tstep, allow_pickle=True)

tstep3, energy3 = [], []
for e, t in home.saved_in_ev:
    tstep3.append(t)
    energy3.append(e)
np.save("paper_results/Conditional_Save_in_Ev.npy", energy3, allow_pickle=True)
np.save("paper_results/Conditional_Ev_save_Time_step.npy", tstep3, allow_pickle=True)

tstep4, energy4 = [], []
for e, t in home.energy_exported:
    tstep4.append(t)
    energy4.append(e)
np.save("paper_results/Conditional_Energy_Exported.npy", energy4, allow_pickle=True)
np.save("paper_results/Conditional_Export_Time.npy", tstep4, allow_pickle=True)

# Plot battery status (Idle, Charging, Discharging)
plt.figure(figsize=(15, 5), dpi=dpi)
plt.plot(status_1, "bp-", linestyle=':', linewidth=2, markersize=10)
plt.plot(status_2, 'r*-', linestyle=':', linewidth=2, markersize=10)
plt.plot(status_3, "go-", linestyle=':', linewidth=2, markersize=10)
plt.plot(status_ev, "^-", linestyle=':', linewidth=2, markersize=10)
plt.xlabel("Time (Hours)", fontsize=fontsize)
plt.legend(["Bat_1 State", 'Bat_2 State', 'Bat_3 State', "EV State"], bbox_to_anchor=(1.0, 1.0, 0.0, 0.15), loc="upper right", ncol=4, fontsize=15)
plt.xticks(np.arange(start_t, end_t+1, 1), fontsize=12)
plt.yticks([0, 1, 2], labels=["Idle", 'Charging', "Discharging"], fontsize=tick_size)
plt.xlim(start_t, end_t)
plt.ylim(-1, 3)
plt.grid()
plt.show()

# Plot EV State of Charge (SOC) and schedule with energy saved in EV
plt.figure(figsize=(15, 5), dpi=dpi)
ax1 = plt.subplot(1, 1, 1)
ax2 = ax1.twinx()
ax3 = ax1.twinx()
ax1.plot(ev_soc, "g*-")
ax2.plot(home.EV.schedule[start_t::], "y--")
ax3.bar(tstep1[start_t::], energy1[start_t::], width=0.35, align="edge", color='blue')
ax3.set_ylabel("Energy (KWh)", fontsize=fontsize)
ax1.set_ylabel("Battery SOC", fontsize=fontsize)
ax1.set_xlabel("Time (Hours)", fontsize=fontsize)
ax1.legend(["EV_Soc"], bbox_to_anchor=(0.0, 1.0, 1.0, 0.15), loc="upper left", ncol=4, fontsize=15)
ax2.legend(["EV_Schedule"], bbox_to_anchor=(0.35, 1.0, 0.0, 0.15), loc="upper right", ncol=4, fontsize=15)
ax1.set_xticks(np.arange(start_t, end_t+1, 4))
ax2.set_yticks([-0.03, 1])
ax2.set_yticklabels(["Home", "Away"], fontsize=fontsize)
plt.xlim(start_t, end_t)
ax1.set_ylim(0, 1.1)
ax2.set_ylim(-1, 1.1)
ax3.set_ylim(0, 10)
ax2.spines["right"].set_position(("axes", 0.0))
ax3.tick_params(axis='y', labelcolor='blue')
ax3.spines["right"].set_position(("axes", 1.0))
ax3.spines["right"].set_edgecolor("blue")
ax3.yaxis.label.set_color("blue")
ax1.grid()
plt.show()

# Define dependencies
dependencies = [
    'numpy',
    'matplotlib',
    'time',
    'Modules',  # Custom module: appliances, EV_, EV_Schedule
    'HEMS_Environment',  # Custom module: home_env
    'MDP_Development1'  # Custom module: HEMS_MDP
]

print("Dependencies:", dependencies)
