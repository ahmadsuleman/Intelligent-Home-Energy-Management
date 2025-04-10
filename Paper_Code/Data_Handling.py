# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 19:35:37 2021

@author: Suleman_Sahib
"""

import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt
import numpy as np

"""
data = pd.read_csv("energy_dataset.csv")
plt.plot(data["price actual"][0:24] )
plt.show()

#np.save("Price_Data.npy",data["price actual"][0:8760], allow_pickle = True )


data = pd.read_csv("PV_GEN.csv")

plt.plot(data["generation"][0:8760] )
plt.show()

#np.save("PV_GEN.npy",data["generation"][0:8760], allow_pickle = True )




8760
 
"""

#Reading device_dataset_2.csv
data = pd.read_csv("device_dataset.csv")
      
print(data.keys())
id_1 = []
always_on = []
d1 = data.loc[data["ID"]== 1]
always_on = d1.loc[d1['Device'] == "AlwaysOn"]
ref_g = d1.loc[d1['Device'] == "Refrigeration"]
wash_m = d1.loc[d1['Device'] == "WashingMachine"]
oven  = d1.loc[d1['Device'] == "Oven"]
dish_w  = d1.loc[d1['Device'] == "DishWasher"]
lights  = d1.loc[d1['Device'] == "Lighting"]
dryer   = d1.loc[d1['Device'] == "Dryer"]
df = dish_w
mean = df['Consumption'].mean()
std = df['Consumption'].std()
outliers = (df['Consumption'] - mean).abs() > std
df[outliers] = np.nan
df['Consumption'].fillna(mean, inplace=True)
dish_w = df
#for ind, ID in enumerate(data["ID"]):
#    if ID == 4: # 4 is good
#        print()    
    #id_1.append(data[ind])
    
    
    #for ind, device in enumerate(data["Device"]):
    #        if device == "AlwaysOn":
    #            if (data['Consumption'][ind] > 4):
    #                always_on.append(np.random.randint(0,3))
    #            else:
    #                always_on.append(data['Consumption'][ind])
    #if (data['ID'] == 1) and (data['Device'] == "AlwaysOn"):
    #    always_on.append(data['Consumption'])
#np.arange(0,len(always_on))        
print("Total Values in Always_on : ", always_on.Consumption.size)
print("Total Values in Refreg    : ",ref_g.Consumption.size)
print("Total Values in wash_M    : ",wash_m.Consumption.size)
print("Total Values in Oven      : ",oven.Consumption.size)
print("Total Values in dish_w    : ",dish_w.Consumption.size)
print("Total Values in lights    : ",lights.Consumption.size)
print("Total Values in dryer     : ",dryer.Consumption.size)


plt.plot(np.arange(0,len(always_on)), always_on['Consumption'])
plt.title("Always On")
plt.show()
plt.plot(np.arange(0,len(ref_g)),ref_g['Consumption'])
plt.title("Ref G")
plt.show()
plt.plot(np.arange(0,len(wash_m)),wash_m['Consumption'])
plt.title("Wash_M")
plt.show()
plt.plot(np.arange(0,len(oven)),oven['Consumption'])
plt.title("Oven ")
plt.show()
plt.plot(np.arange(0,len(dish_w)),dish_w['Consumption'])
plt.title("Dish_W")
plt.show()
plt.plot(np.arange(0,len(lights)),lights['Consumption'])
plt.title("Lights")
plt.show()
plt.plot(np.arange(0,len(dryer)),dryer['Consumption'])
plt.title("Dryer")
plt.show()


plt.plot(np.arange(0,24),wash_m['Consumption'][0:24])
plt.title("Wash M")
plt.show()
plt.plot(np.arange(0,24),oven['Consumption'][0:24])
plt.title("oven")
plt.show()
plt.plot(np.arange(0,24),dish_w['Consumption'][0:24])
plt.title("Dish_W")
plt.show()
plt.plot(np.arange(0,24),lights['Consumption'][0:24])
plt.title("lights")
plt.show()
plt.plot(np.arange(0,24),dryer['Consumption'][0:24])
plt.title("Dryer")
plt.show()

"""
#Reading device_dataset.csv
data = pd.read_csv("device_dataset.csv")
light = []
ID = "Lighting" # "Refrigeration" 

for ind, device in enumerate(data['Device']):
    if device == ID:
        light.append(data["Consumption"][ind])

for ind, d in enumerate(light):
    if d >10:
        light[ind] = 0        
plt.plot(light[0:96])
plt.show()
"""