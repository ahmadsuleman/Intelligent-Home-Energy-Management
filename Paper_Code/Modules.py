# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 14:12:47 2021

@author: Suleman_Sahib
"""
import numpy as np
import pandas as pd
dataset = pd.read_csv("dataset_hourly.csv")

#print(dataset.keys())
class Battery_:
    def __init__(self, size, eta = 0.95):
        self.size = size 
        self.eta  = eta
        self.soc  =  0
        self.state = 0
        self.status = 0
        self.soc_plot = []
        self.time_step = []
        self.curtail_amount = []
        self.load_curtail = 0
        self.curtail_ = 0
        self.soc_plot.append(self.soc)
        self.time_step.append(0)
        
    def reset(self):
        self.soc  =  0
        self.state = 0
        self.status = 0
        self.load_curtail = 0
        self.curtail_ = 0
        #self.soc_plot = []
        #self.time_step = []
        self.curtail_amount = []

    def charge(self, energy, t):
         # Charging
        self.curtail_ = 0
        if (self.soc < 1) and (self.status != 1) :
            self.state = 1 # Under charging.  Flag --> 
            
            storable = 1 -  self.soc 
            required_for_storage = storable * self.size/ self.eta
            required_for_storage = round(required_for_storage,3)
            
            if (required_for_storage > energy):
                self.soc += (energy/ self.size) * self.eta
                self.soc = round(self.soc, 3)
            else:
                self.soc += round(required_for_storage/ self.size * self.eta , 3)
                self.soc = round(self.soc, 3)
                self.state = 0
                self.status = 1
                self.curtail_ = round (energy - required_for_storage, 3)
        else:
            self.state = 0
            #self.status = 1
        #self.curtail_amount.append(curtail_)
        #self.soc_plot.append(self.soc)
        #self.time_step.append(t)
        
    def drain(self, load, t):
        self.load_curtail = 0
        if self.state == 1:
            print("... Battery is under charging ...")
        elif (self.soc > 0.2) or (self.status == 1):
            self.state = 2
            dischargable = self.soc - 0.2
            dischargable = round(dischargable, 3)
            #print(f"storable energy {storable}")
            required_from_battery = round (load/self.size/ self.eta, 3)
            if (required_from_battery <= dischargable):
                self.soc -= required_from_battery 
            else:
                self.load_curtail =  required_from_battery - dischargable
                self.soc -= dischargable
                self.state = 0
                self.status = 0
        else:
            print("... Battery is empty ...")
            
        #self.soc_plot.append(self.soc)
        #self.time_step.append(t)        
        
class EV_:
    def __init__(self, size, eta = 0.95):
        self.size = size 
        self.eta  = eta
        
        self.soc  =  0.2
        self.state = 0
        self.status = 0
        self.soc_plot = []
        self.time_step = []
        self.curtail_amount = []
        self.load_curtail = 0
        self.curtail_ = 0
        self.soc_plot.append(self.soc)
        self.time_step.append(0)
        
    def reset(self):
        self.soc  =  0.2
        self.state = 0
        self.status = 0
        self.load_curtail = 0
        self.curtail_ = 0
        #self.soc_plot = []
        #self.time_step = []
        self.curtail_amount = []

    def charge(self, energy, t):
         # Charging
        self.curtail_ = 0
        if (self.soc < 1):
            self.state = 1
            storable = 1 -  self.soc
            required_for_storage = storable * self.size/ self.eta
            required_for_storage = round(required_for_storage,3)
            if (required_for_storage > energy):
                self.soc += (energy/ self.size) * self.eta
                self.soc = round(self.soc, 3)
                
            else:
                self.soc += round(required_for_storage/ self.size * self.eta , 3)
                self.soc = round(self.soc, 3)
                self.state = 0
                self.status = 1
                self.curtail_ = round (energy - required_for_storage, 3)
                
        else:
            self.state = 0
            self.status = 1
        #self.curtail_amount.append(curtail_)
        #self.soc_plot.append(self.soc)
        #self.time_step.append(t)
        
    def drain(self, load, t):
        self.load_curtail = 0
        #if self.state == 1:
        #    print("... Battery is under charging ...")
        if (self.soc > 0.2):
            self.state = 2
            dischargable = self.soc - 0.2
            dischargable = round(dischargable, 3)
            #print(f"storable energy {storable}")
            required_from_battery = round (load/self.size/ self.eta, 3)
            if (required_from_battery <= dischargable):
                self.soc -= required_from_battery
                self.status = 0
            else:
                self.load_curtail =  required_from_battery - dischargable
                self.soc -= dischargable
                self.state = 0
                self.status = 0
        else:
            #print("... Battery is empty ...")
            self.state = 0
            self.status = 0
        #self.soc_plot.append(self.soc)
        #self.time_step.append(t)         
        
const = 3        
class PV_:
    def __init__(self, capacity = 20000):
        #energy = np.load('PV_GEN.npy', allow_pickle=True)
        #self.pv_dataset = energy*capacity # maximum 100 MW
        self.pv_dataset = round ((dataset["solar"]/max(dataset["solar"]))*capacity, 1)
        #self.capacity = capacity
        
    def gen(self, time_step):
        return self.pv_dataset[time_step]/1000
    
class Price_Data:
    def __init__(self, capacity =1):
        #price = np.load('Price_Data.npy', allow_pickle=True)
        #self.current_price = price# maximum 100 MW
        self.price_dataset = dataset["Price_Data"] /max(dataset["Price_Data"]) * 0.45
        self.price_dataset_1 = dataset["Price_Data_1"] /max(dataset["Price_Data_1"])

    def price(self, time_step):
        return self.price_dataset[time_step]

class EV_Schedule:
    def __init__(self, capacity =1):
        #price = np.load('Price_Data.npy', allow_pickle=True)
        #self.current_price = price# maximum 100 MW
        self.schedule = dataset["car_schedule"]

    def at_home(self, time_step):
        return self.schedule[time_step]
    
class appliances:
    def __init__(self):
        
        self.dishwasher = dataset["dishwasher1"]/max(dataset["dishwasher1"]) * 1200
        self.washingmachine = (dataset["clotheswasher1"]/max(dataset["clotheswasher1"]) ) * 1000
        self.clothesdryer = dataset["drye1"]/max(dataset["drye1"])* 3500
        self.hvac = dataset["air1"]/max(dataset["air1"]) * 3517 
        
        self.ref    = (dataset["refrigerator1"]/max(dataset["refrigerator1"]) )* 400
        #self.heater = dataset["heater1"]/max(dataset["heater1"]) * 4500
        self.microwave = dataset["microwave1"]/max(dataset["microwave1"])*600
        #self.water_pump = dataset["pump1"]/max(dataset["pump1"])*1200
        self.lights  = dataset["lights_plugs1"]/max(dataset["lights_plugs1"]) * 90
        #self.appliance_list = ["dishwasher", "washingmachine", "clothesdryer", "hvac", "ref", "heater", "microwave", "water_pump","lights"]
        
        #self.ap_status = [0,0,0,0,0]
        
        #self.schedule = []
        #np.random.seed(342)
        
    

        
    def load(self,timestep):
        
        load = 0
        load += self.dishwasher[timestep]
        load += self.washingmachine[timestep]
        load += self.clothesdryer[timestep]
        load += self.hvac[timestep]
        load += self.ref[timestep]
        #load += self.heater[timestep]
        load += self.microwave[timestep]
        #load += self.water_pump[timestep]
        load += self.lights[timestep]
        
        return load/1000
       
#for i, data in enumerate(dataset["Price_Data_1"]):
#    if data > 0.35:
#        print(dataset["Price_Data_1"][i])# = 0.35
#dataset["Price_Data_1"] = dataset["Price_Data_1"]
#dataset.to_csv("dataset_hourly.csv")


# Dataset Plots
"""
import matplotlib.pyplot as plt 

endt = 48

pv = PV_()
ap = appliances()
price = Price_Data()
data = pv.pv_dataset[0:endt]
fontsize = 18
leg_font = 15
load = []
tick_font = 13


 
for i in range (endt):
       load.append(ap.load(i))
 
print(max(ap.ref[0:endt]))       

plt.figure(figsize=((12,5)), dpi=300)
#fig.title("Appliance Consumption and Power Ratings")   
plt.subplot(4, 2, 1)
plt.plot(ap.ref[0:endt]/1000, "p-", color='green')
plt.legend(["Refrigerator (0.4 KW)"], fontsize=leg_font, bbox_to_anchor=(0.0, 1.0, 1.0, 0.3),loc="upper left")
plt.ylim(0.1,0.3)
plt.xlim(0,endt-1)
#plt.ylabel("Energy (KWh)", fontsize=fontsize)
plt.xticks([])
plt.yticks([0.1,0.2,0.3], fontsize=tick_font)


plt.subplot(4, 2, 2)
plt.plot(ap.hvac[0:endt]/1000, "p-", color='green')
plt.legend(["Air Conditioner (3.5 KW)"], fontsize=leg_font, bbox_to_anchor=(0.0, 1.0, 1.0, -0.1),loc="center")
plt.ylim(0,1.5)
plt.xlim(0,endt-1)
plt.yticks([0,0.75,1.5], fontsize=tick_font)
#plt.ylabel("Energy (KWh)", fontsize=fontsize)
plt.xticks([])
plt.subplot(4, 2, 3)
plt.plot(ap.dishwasher[0:endt]/1000, "p-",color='green')
plt.legend(["Dishwasher (1.2 KW)"], fontsize=leg_font, bbox_to_anchor=(0.0, 1.0, 1.0, 0.26),loc="upper left")
plt.xticks([])
plt.ylim(0,0.75)
plt.xlim(0,endt-1)
plt.yticks([0,0.35,0.75], fontsize=tick_font)

plt.ylabel("Energy (KWh)", fontsize=fontsize, loc='top')
plt.subplot(4, 2, 4)
plt.plot(ap.washingmachine[0:endt]/1000, "p-", color='green')
plt.legend(["Washing Macine (1 KW)"], fontsize=leg_font, bbox_to_anchor=(0.0, 1.0, 1.0, -0.1),loc="center")
plt.xticks([])
plt.ylim(0,0.5)
plt.xlim(0,endt-1)
plt.yticks([0,0.25,0.5], fontsize=tick_font)
#plt.ylabel("Energy (KWh)", fontsize=fontsize, loc='top')
plt.subplot(4, 2, 5)
plt.plot(ap.microwave[0:endt]/1000, "p-", color='green')
plt.legend(["Microwave (0.6 KW)"], fontsize=leg_font, bbox_to_anchor=(0.0, 1.0, 1.0, 0.26),loc="upper left")
plt.ylim(0,0.3)
plt.xlim(0,endt-1)
plt.yticks([0,0.15,0.3], fontsize=tick_font)
#plt.ylabel("Energy (KWh)", fontsize=fontsize)
plt.xticks([])
plt.subplot(4, 2, 6)
plt.plot(ap.lights[0:endt]/1000, "p-", color='green')
plt.legend(["Lightining (0.9 KW)"], fontsize=leg_font, bbox_to_anchor=(0.0, 1.0, 1.0, -0.1),loc="center")
plt.ylim(0,0.06)
plt.xlim(0,endt-1)
plt.yticks([0,0.03,0.06], fontsize=tick_font)
#plt.ylabel("Energy (KWh)", fontsize=fontsize)
plt.xticks([])
plt.subplot(4, 2, 7)
plt.plot(ap.clothesdryer[0:endt]/1000, "p-",color='green')
plt.legend(["Cloth Dryer (3.5 KW)"], fontsize=leg_font, bbox_to_anchor=(0.0, 1.0, 1.0, 0.26),loc="upper left")
plt.ylim(0,2)
plt.xlim(0,endt-1)
plt.yticks([0,1,2], fontsize=tick_font)

plt.xticks(np.arange(0,endt+1, 8), fontsize=tick_font)
#plt.ylabel("Energy (KWh)", fontsize=fontsize)
plt.xlabel("Time (Hours)", fontsize=fontsize)

plt.subplot(4, 2, 8)
plt.plot(load[0:endt], "p-", color='green')
plt.legend(["House Consumption (5 KW)"], fontsize=leg_font, bbox_to_anchor=(0.0, 1.0, 1.0, 0.0),loc="center")
plt.ylim(0,3)
plt.xlim(0,endt-1)
plt.yticks([0,1.5,3], fontsize=tick_font)
plt.xticks(np.arange(0,endt+1, 8), fontsize=tick_font)
#plt.ylabel("Energy (KWh)", fontsize=fontsize)
plt.xlabel("Time (Hours)", fontsize=fontsize)


#plt.show()


#.savefig("paper_results/Compltet Dataset Plot.png",bbox_inches='tight',pad_inches = 0, transparent=True)
"""
