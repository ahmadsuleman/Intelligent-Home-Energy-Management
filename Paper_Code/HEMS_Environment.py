# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 15:32:07 2021

@author: Suleman_Sahib
"""

from Modules import Battery_, EV_, PV_, appliances, Price_Data, EV_Schedule


ev_ch_cap = 7.400
class home_env:
 
     def __init__(self, Total_Battries = 3, Total_EV = 1):
         
         self.pv = PV_()
         
         self.gen = 0
         self.load = 0
         self.grid_util = 0
         self.gen_load = 0
         self.energy_exported = []
         self.grid_cost = []
         self.imported_from_grid = []
         self.saved_in_batteries = []
         self.used_from_batteries = []
         self.saved_in_ev = []
         self.ev_profit = []
         self.generation = []
         self.consumption = []
         self.profit = []
         self.ev_profit = []
         self.EV = EV_Schedule()
         
         self.grid_price = Price_Data()
         
         
         
         self.bat_no = 0
         self.drain_no = 0
         self.charge_count = 0
         self.total_bat = Total_Battries
         
         
         self.battries = [Battery_(size=15) for _  in range(Total_Battries)]
         
         self.ev = EV_(size=20.000)
         self.appliances = appliances()
         
     
     def reset(self):
         self.ev.reset()
         for b in self.battries:
             b.reset()
         
         self.bat_no = 0
         self.drain_no = 0
         self.charge_count = 0
         self.grid = 0
         self.gen = 0
         self.load = 0
         self.gen_load = 0
         
     def data_reset(self):    
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
         self.ev_profit = []
     
     # This method is used for managing energy through reinforcemenet learning 
     # 
     def get_energy(self, t):
         self.gen = self.pv.gen(t)
         self.load = self.get_load(t)
         self.generation.append((self.gen, t))
         self.consumption.append((self.load, t))
         
         if (self.gen > self.load):
             energy = self.gen - self.load
             self.gen_load = 1 
             # this shows that energy is available after fulfilling the load 
         else:
             energy = self.load - self.gen
             self.gen_load = 0
             # this shows that energy is not available after fulfilling the load
         #self.generation.append((self.gen,t))
         #self.consumption.append((self.load,t))
         return energy, self.gen_load
         
     
     # This function automatically manages all the energy routing 
     # Using rule based method 
     #

         #self.profit = self.ev_profit - self.cost    
             
#This method returns the load consumed by all the appliances at home.
     def get_load(self, timestep):
         return self.appliances.load(timestep)
     
     def save_in_battery(self, energy, t):

         if (self.battries[0].status != 1) or (self.battries[1].status != 1) or (self.battries[2].status != 1) : 
            #print("Battery being charged------------------", self.bat_no)
            #self.saved_in_batteries.append((energy, t))
            self.battries[self.bat_no].charge(energy, t)
            self.saved_in_batteries.append((energy, t))
            
            if self.battries[self.bat_no].status == 1:
               
                ex = self.battries[self.bat_no].curtail_
                for no, b in enumerate(self.battries):    
                    if b.status == 0:
                        self.bat_no = no
                        break
                self.battries[self.bat_no].charge(ex, t)
                    
                ex = 0
         else:
            #print ("All battries are Full", self.bat_no)
            
            self.bat_no = 0
            for no, b in enumerate(self.battries):    
                    if b.status == 0:
                        self.bat_no = no
                        break
            
     
     def drain_from_battery(self, energy, t):
        
        if (self.battries[0].status == 1) or (self.battries[1].status == 1) or (self.battries[2].status == 1) :    
            #self.used_from_batteries.append((energy,t))
            if (self.battries[self.drain_no].status == 0):
                #self.charge_count -= 1
                
                for no, b in enumerate(self.battries):    
                    if b.status == 1:
                        self.drain_no = no
                        break
            #print("Battery being Drained is ....Drain#------------. ",self.drain_no , self.battries[self.drain_no].status )
            
            if (self.battries[self.drain_no].status != 0):
                self.battries[self.drain_no].drain(energy, t)
                self.used_from_batteries.append((energy, t))
                profit = energy * self.grid_price.price(t)
                self.profit.append((profit, t))
                
                
           # print("here inside", self.drain_no)
        else: # All batteries empty condition
            #print(f"{energy} KW Energy will be taken from grid")
            
            for no, b in enumerate(self.battries):    
                    if b.status == 1:
                        self.drain_no = no
                        break
        
     
     def manage_energy(self, time_step):
         
         t = time_step
         self.gen = self.pv.gen(t)
         self.load = self.get_load(t)
         self.generation.append((self.gen,t))
         self.consumption.append((self.load,t))
         self.get_energy(t)
         #print(gen, load)
         if self.gen > self.load:
             energy = self.gen - self.load
             if (self.battries[0].soc < 1) or (self.battries[1].soc < 1) or (self.battries[2].soc < 1) :
                 self.save_in_battery(energy, t)
                 
             elif (energy >= ev_ch_cap) and (self.ev.soc < 1) and (self.EV.at_home(t) == 0):
                     self.gen_load = 1
                     self.charge_ev(0, t)
                     
                     
             else:
                 self.export_energy(energy, t)
                 
                    
         else:
             energy = self.load - self.gen
             if (self.battries[0].status == 1) or (self.battries[1].status == 1) or (self.battries[2].status == 1) :
                 self.drain_from_battery(energy, t)
                 self.used_from_batteries.append((energy,t))
                 if (self.ev.status < 0.8) and (self.EV.at_home(t) == 0):
                     self.charge_ev(energy, t)
                     #self.saved_in_ev.append((5,t))
                     self.drain_from_battery(ev_ch_cap, t)
                     
                 
             else:
                 self.get_from_grid(energy, t)
                 #self.imported_from_grid.append((energy,t))
                 if (self.ev.status < 0.8) and (self.EV.at_home(t) == 0):
                     self.charge_ev(energy, t)
                     #self.saved_in_ev.append((5,t))
                     self.get_from_grid(ev_ch_cap, t)
                     #self.imported_from_grid.append((5,t))
                
             
         
         if (self.EV.at_home(t) == 1):
            self.ev.drain(2.265,t)
     def get_from_grid(self, load, t):
         cost = load * self.grid_price.price(t)
         self.grid_util = load 
         self.grid_cost.append((cost,t))
         self.imported_from_grid.append((load,t))
         
         
     def export_energy(self, energy, t):
         profit_now = energy * self.grid_price.price(t)
         self.energy_exported.append((energy, t))
         self.profit.append((profit_now , t))
         
         
     def charge_ev(self,energy, t):
             # EV is charged at constant rate that is 3 KW energy per hour. 
             ### if energy passed to this function is extra solar energy then only 
             # 3Kw is passed to EV battery and other is exported to the grid.
             ### Othsewise: 3Kw is drained form home battery and saved in EV battery 
             profit = 0
             if (self.gen_load == 1):
                 if (energy ==  ev_ch_cap):
                    self.ev.charge(ev_ch_cap, t)
                    self.saved_in_ev.append((ev_ch_cap,t))
                    profit = ev_ch_cap * self.grid_price.price(t)
                    self.ev_profit.append((profit, t))
                    self.profit.append((profit, t))
                    
                 elif (energy > ev_ch_cap):
                    extra = energy - ev_ch_cap
                    self.ev.charge(ev_ch_cap, t)
                    self.saved_in_ev.append((ev_ch_cap,t))
                    profit = ev_ch_cap * self.grid_price.price(t)
                    self.ev_profit.append((profit, t))
                    self.profit.append((profit, t))
                    self.export_energy(extra, t)
                 elif (energy < ev_ch_cap):
                     remain = ev_ch_cap - energy
                     
                     self.ev.charge(ev_ch_cap, t)
                     self.saved_in_ev.append((ev_ch_cap,t))
                     cost = remain * self.grid_price.price(t)
                     personal = energy *  self.grid_price.price(t)
                     profit = personal - cost
                     self.ev_profit.append((profit, t))
                     self.profit.append((profit, t))
                     self.get_from_grid(remain, t)
             
             else:
                 if (self.battries[0].status == 1) or (self.battries[1].status == 1) or (self.battries[2].status == 1):
                     self.ev.charge(ev_ch_cap, t)
                     self.saved_in_ev.append((ev_ch_cap,t))
                     self.drain_from_battery(ev_ch_cap + energy, t)
                     profit = ev_ch_cap * self.grid_price.price(t)
                     self.ev_profit.append((profit, t))
                     #self.profit.append((profit, t))
                 else:
                     self.get_from_grid(ev_ch_cap + energy, t)
                     self.ev.charge(ev_ch_cap, t)
                     self.saved_in_ev.append((ev_ch_cap,t))
                     profit = -ev_ch_cap * self.grid_price.price(t)
                     self.ev_profit.append((profit, t))
                     self.profit.append((profit, t))
                     
                 
                     
                     

        
"""

     def manage_energy(self, time_step):
         
         t = time_step
         self.gen = self.pv.gen(t)
         self.load = self.get_load(t)
         self.generation.append((self.gen,t))
         self.consumption.append((self.load,t))
         #print(gen, load)
         if self.gen > self.load:
             energy = self.gen - self.load
             if (self.battries[0].soc < 1) or (self.battries[1].soc < 1) or (self.battries[2].soc < 1) :
                 self.save_in_battery(energy, t)
                 self.saved_in_batteries.append((energy,t))
             
             elif (self.ev.status != 1) and (self.EV.at_home(t) == 0):
                     self.charge_ev(energy, t)
                     #self.saved_in_ev.append((energy,t))
             else:
                 self.export_energy(energy, t)
                 
                    
         else:
             energy = self.load - self.gen
             if (self.battries[0].status == 1) or (self.battries[1].status == 1) or (self.battries[2].status == 1) :
                 self.drain_from_battery(energy, t)
                 self.used_from_batteries.append((energy,t))
                 if (self.ev.status != 1) and (self.EV.at_home(t) == 0):
                     self.charge_ev(energy, t)
                     #self.saved_in_ev.append((energy,t))
                 
             else:
                 self.get_from_grid(energy, t)
                 #self.imported_from_grid.append((energy,t))
                 if (self.ev.status < 0.5) and (self.EV.at_home(t) == 0):
                     self.charge_ev(5, t)
                     #self.saved_in_ev.append((5,t))
                     self.get_from_grid(5, t)
                     #self.imported_from_grid.append((5,t))
                
             
         
         if (self.EV.at_home(t) == 1):
            self.ev.drain(0.6,t)
            
"""