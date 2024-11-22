import os
import glob
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


import os

print('ds')



chanstr = 'C08' #C08, C09, C10, C13


mo_no = [0, 31,28,31,30,31,30,31,31,30]
num_day=np.cumsum(mo_no)
day_no = np.arange(273)


ld = 0

rad_vecs=[]
time_list=[]
for day in day_no:
    if day == num_day[ld+1]:

        ds = xr.Dataset(
    data_vars=dict(
    rad_vecs=(["time","len"], rad_vecs)
    ),
    coords=dict(
    time=time_list,
    len = np.arange(97714)
    ),
    attrs=dict(description="ABI radiance vectors"),
    )
    
        ds.to_netcdf(chanstr+"vectors"+str(ld+1)+".nc")
        rad_vecs=[]
        time_list=[]
        ld += 1
        
    for i in range(len(sorted(glob.glob('#directory/noaa-goes16/ABI-L1b-RadF/2018/'+format(day+1,'03')+'/*/*'+chanstr+'*')):
            if i == 0:
                C08 = sorted(glob.glob('#directory/noaa-goes16/ABI-L1b-RadF/2018/'+format(day+1,'03')+'/*/*'+chanstr+'*'))[i]
                ds=xr.open_dataset(C08)
                mask1 = (ds.x > -0.088) & (ds.x < -0.053) & (ds.y >= 0.112) & (ds.y < 0.123)
                mask2 = (ds.x > -0.1) & (ds.x < -0.023) & (ds.y >= 0.093) & (_ds.y < 0.112)
                mask3 = (ds.x > -0.1) & (ds.x < 0) & (ds.y >= 0.07) & (ds.y < 0.093)
                mask4 = (ds.x > -0.063) & (ds.x < 0) & (ds.y > 0.058) & (ds.y < 0.07)
    
                mastermask = mask1 | mask2 | mask3 | mask4
                c8dat=xr.open_dataset(C08)
    
                td=datetime.strptime(c8dat.attrs['date_created'], '%Y-%m-%dT%H:%M:%S.%fZ')
                td= td.strftime('%Y-%m-%d-%H:%M:%S')
                time_list.append(td)
                t=np.where(mastermask.T == True, c8dat['Rad'],-999)
                radiance_vector=t[t != -999]  
                radiance_vector = radiance_vector[::16]
                rad_vecs.append(radiance_vector)


            else:
                C08 = sorted(glob.glob('#directory/noaa-goes16/ABI-L1b-RadF/2018/'+format(i+1,'03')+'/*/*'+chanstr+'*'))[i]
                c8dat=xr.open_dataset(C08)
                td=datetime.strptime(c8dat.attrs['date_created'], '%Y-%m-%dT%H:%M:%S.%fZ')
                td=td.strftime('%Y-%m-%d-%H:%M:%S')
                time_list.append(td)
                rad=c8dat['Rad']*mastermask
                t=np.where(mastermask.T == True, c8dat['Rad'],-999)
                radiance_vector=t[t != -999]  
                radiance_vector = radiance_vector[::16]
                rad_vecs.append(radiance_vector)

