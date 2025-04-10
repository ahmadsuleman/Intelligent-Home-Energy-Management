# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 14:12:47 2021

@author: Suleman_Sahib
"""
import gym 
from gym import Env,spaces
import matplotlib.pyplot as plt
import numpy as np

from Modules import PV_, EV_Schedule
from HEMS_Environment import home_env

#observation_space = spaces.Box(low=np.array([0,0,0,0,0]), high=np.array([1.0,1.0,1.0, 100,1.0]))
#print(observation_space.shape)


"""
Action Space: Discrete (Charge Battery, charge ev, discharge battery, import from grid, turn_off_load)
Observation Space: Continuous (All_bat_soc, pv, load, ev_state)
"""
class HEMS_MDP(Env):
    def __init__(self):
        
        self.action_space = spaces.Discrete(5)
        self.observation_shape = (6,)
        self.observation_space = spaces.Box(low=np.array([0,0,0,0,0,0]), high=np.array([1,1,1,1,1,1]))
        PV = PV_()

        self.home = home_env()
        self.time_step = 0
        self.EV = EV_Schedule()
        self.steps_in_environment = 0
        self.episode_reward = 0
        
        self.energy_exported = []
        self.grid_cost = []
        self.imported_from_grid = []
        self.saved_in_batteries = []
        self.used_from_batteries = []
        self.saved_in_ev = []
        self.ev_profit = []
        self.profit = []
        self.generation = []
        self.consumption = []
       
        
    def step(self, action):
        reward = 0
        done = False
        # gen_or_load: It is true if generation is more than load else False
        # energy: It is the amount of extra load or extra generation 
        # energy = generation - load     [ if generation > load ] (It is also considerd as extra energy) 
        # energy = load - generation     [ if load > generation ]
        energy, gen_or_load = self.home.get_energy(self.time_step)
        
        
        if action == 0:  # Charge the battery
            # It saves the energy to the battery without checking any condition. 
            # Because it is the responsibility of the RL agent to correctly monitor the state
            # and chose correct action
            
            
            
            
            # A reward +ve reward is awarded if the batteries are charges with the energy that is extra 
            # after fulfilling the load. Batteries are only charged from the soalr energy available to save 
            # the cost. 
            # a negative reward is awarded by the environment for charging the batteries at wrong state.
            #self.home.save_in_battery(energy, self.time_step)
            #self.saved_in_batteries.append((energy,self.time_step))
            if (gen_or_load == 1) and ((self.home.battries[0].status != 1) or (self.home.battries[1].status != 1) or (self.home.battries[2].status != 1)):
                self.home.save_in_battery(energy, self.time_step)
                reward += 1.0
                
            else:
                reward -= 1.0
        
        # Charge the EV
        if action == 1:
            # Ev is charged either from the extra energy or from the batteries. 
            # Positive Reward conditions are 
            #   if EV is not full
            #   if any battery among all batteries is fully charged 
            #   if EV is at home.
            # if any one of the conditions is not fulfilled negative reward is given
            #self.home.charge_ev(energy, self.time_step)
            #self.saved_in_ev.append((energy,self.time_step))
            
            if (self.home.ev.status != 1) and (self.EV.at_home(self.time_step) == 0): 
                
                self.home.charge_ev(energy, self.time_step)
                reward += 2.5
                #done = True
            else:
                reward -= 1.0   
        #Discharge the battery
        if action == 2:
            # For positive reward
            # Batteries must be discharged when the load is greater than generation. 
            #  and an one of the battery is fully charged. 
            #self.home.drain_from_battery(energy,self.time_step)
            #self.used_from_batteries.append((energy,self.time_step))
            if (gen_or_load == 0) and ((self.home.battries[0].status == 1) or (self.home.battries[1].status == 1) or (self.home.battries[2].status == 1)):
                
                self.home.drain_from_battery(energy,self.time_step)
                reward += 1.0
                #done = True
            else:
                reward -= 1.0
        #Import from Grid        
        if action == 3:
            # To get positive reward
            # Energy must be imported from grid if the load is greater than generation 
            # and all the batteries are fully drained. 
            #self.home.get_from_grid(energy,self.time_step)
            #self.imported_from_grid.append((energy,self.time_step))
            if (gen_or_load == 0) and (self.home.battries[0].status == 0) and (self.home.battries[1].status == 0) and (self.home.battries[2].status == 0):
                
                self.home.get_from_grid(energy,self.time_step)
                reward += 1.0
                #done = True
            else:
                reward -= 1.0
            
        #Export Energy to the grid
        if action == 4:
            # A positive reward for export will be given if generation is greater than load
            # all the batteries are fully charged and EV if fully charged or EV is not at home. 
            # 
            #self.home.export_energy(energy, self.time_step)
            #self.energy_exported.append((energy,self.time_step))
            if (gen_or_load == 1) and (self.home.battries[0].status == 1 and self.home.battries[1].status == 1  and self.home.battries[2].status == 1) and ((self.EV.at_home(self.time_step) == 1) or ((self.EV.at_home(self.time_step) == 0) and (self.home.ev.status == 1))):
                
                self.home.export_energy(energy, self.time_step)
                
                reward += 1.0
                #done = True
            else:
                reward -= 1.0
            #else:
            #    act_reward = -1.0
                #done = True
            # done = True means that the ultimate goal of the agnet is to fully charge all the batteries and EV battery and start exporting the extra energy to the grid. 4.0
        
        # It is the utilization of EV battery when EV is not at home.
        # EV battery is drained at a constant rate 
        
        
        if (self.EV.at_home(self.time_step) == 1):
            self.home.ev.drain(2.265,self.time_step)
        
        
        
        if reward == 1:
            self.episode_reward += 1
        if (self.steps_in_environment >= 36):
            done = True
            reward = self.episode_reward #1000
            self.episode_reward = 0
            self.steps_in_environment  = 0.0
        else:
            self.steps_in_environment += 1
            
                    
        #self.time_step += 1
        next_state = self.get_next_state()
        # The dataset contains 6 months of data. So there are 4416 hours in 6 months. 
        # Thus after every 4415 hours values from dataset will be loaded again from first hour.  
        if self.time_step == 4414:
            self.time_step = 0
        else: 
            self.time_step += 1
            
        
        
        
        
        return next_state, reward, done, {}
        

        
        
        
    def get_next_state(self):
        
        energy, gen_or_load = self.home.get_energy(self.time_step + 1)
        b1 = self.home.battries[0].status 
        b2 =  self.home.battries[1].status 
        b3 = self.home.battries[2].status 
        state_ev = self.home.ev.status
        home_status = self.EV.at_home(self.time_step + 1)
        return np.asarray([gen_or_load, b1,b2,b3, state_ev, home_status])
        
        
        
        
    def reset(self):
        self.home.reset()
        #self.home.data_reset()
        self.steps_in_environment = 0 
        self.episode_reward = 0.0
        energy, gen_or_load = self.home.get_energy(self.time_step)
        b1 = self.home.battries[0].status 
        b2 =  self.home.battries[1].status 
        b3 = self.home.battries[2].status 
        state_ev = self.home.ev.status
        home_status = self.EV.at_home(self.time_step)
        return np.asarray([gen_or_load, b1,b2,b3, state_ev, home_status])
    
    def close(self):
        pass
        
"""
env = HEMS_MDP()


for t in range(5000):
    a = env.action_space.sample()
    n_state, reward, done, _ = env.step(a)
    
    if (done == True) and reward > 0:
        print(reward)
        
"""