import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from library import *

##################################
###MAIN CODE
##################################

# Selected levels to build climatology
vlev=[0., 10., 20., 40., 60., 80., 100., 120., 140., 160., 200., 250., 300., 400., 500., 600., 700., 800., 900., 1000., 1100., 1200., 1300., 1400., 1600., 1800., 2000., 2200., 2400., 2600., 2800., 3000., 3200., 3400., 3600., 3800., 4000., 4200.]

Nlev=len(vlev)
delta=np.zeros(Nlev)
for k in range(Nlev):
    if vlev[k] <= 5.:
       delta[k]=5. 
    if (vlev[k] >5.) and (vlev[k] <= 160.):
       delta[k]=5. 
    if (vlev[k] > 160.) and (vlev[k] <= 300.):
       delta[k]=5. 
    if (vlev[k] > 300.) and (vlev[k] <= 1400.):
       delta[k]=10. 
    if (vlev[k] > 1400.): 
       delta[k]=20. 


bins_limit=np.zeros(Nlev+1)

bins_limit[0]=0.
for k in range(1,Nlev):
    bins_limit[k] = 0.5*(vlev[k-1]+vlev[k])
bins_limit[Nlev] = 0.5*(vlev[Nlev-1]+12000.)

print(bins_limit)

dirplots='PLOTS'
crdir(dirplots)

dir_gotm_txt='GOTM_INPUT'
crdir(dir_gotm_txt)

dir_gotm_clim_txt='GOTM_INPUT_CLIM'
crdir(dir_gotm_clim_txt)

df0 = pd.read_csv("DATA_BATS/bats_bottle.txt", sep="\t",skiprows = 59, engine='python')

#ordering data for ascending date and ascending depth
# yyyymmdd
# Depth positive downward

df = df0.sort_values(['yyyymmdd', 'time', 'Depth'], ascending=[True, True, True])

#-----------------------

#var_list=['Temp', 'Sal1','Sig-th','NO21','NO31', 'PO41','O2(1)','CO2', 'Alk','Si1','POC','PON','POP']
detection_limit={'NO21':0.01, # mmol/m3
                 'NO31':0.05, # mmol/3
                 'PO41':0.01, # mmol/m3
                 'O2(1)':0.5, # umol/kg --> assume is also umol/L
                 'CO2':0.0,   
                 'Alk':0.0,
                 'Si1':0.1,   # mmol/m3
                 'POC':0.5,   # ug/Kg --> assume it is also ug/L
                 'PON':0.5/14., # umol/Kg --> assume is umol/L
                 'POP':0.01,
                 'Chl':0.001,
                 'TDP':0.01,
                 'TOC':np.nan,
                 'TN':0.05,
                 'Temp': np.nan,
                 'Sal1': np.nan,
                 'Sig-th':np.nan} 

bottom_fill={'NO21':True, # if false set bottom value to zero
                 'NO31':True, 
                 'PO41':True, 
                 'O2(1)':True,
                 'CO2':True,
                 'Alk':True,
                 'Si1':True,   
                 'POC':False,  
                 'PON':False, 
                 'POP':False,
                 'Chl':False,
                 'TDP':True,
                 'TOC':True,
                 'TN':True,
                 'Temp': True,
                 'Sal1': True,
                 'Sig-th':True} 

var_list=['Temp', 'Sal1','Sig-th','NO21','NO31', 'PO41','O2(1)','CO2', 'Alk','Si1','POC','PON','POP']
for var in var_list:

   samp_date_hist(df,var, dirplots)
   samp_depth_hist(df,var, dirplots)

#  dump_gotm_file(df,var, dir_gotm_txt)

month_list=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
            'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

#month_list=['JAN']


#### Create climatology
ymin=2009
ymax=2020
# Variables with no unit conversion

# Temperature
print("processing var : Temperature")
var='Temp'
Temp=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
dump_gotm_monthly_clim_file(Temp,ymin,ymax,vlev,var,month_list,bottom_fill[var],dir_gotm_clim_txt)

# Salinity
print("processing var : Salinity")
var='Sal1'
Sal1=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
dump_gotm_monthly_clim_file(Sal1,ymin,ymax,vlev,var,month_list,bottom_fill[var],dir_gotm_clim_txt)

# Density scaling using in-situ computed density from T and S
print("processing var : RHO")
RHO=np.zeros((12,Nlev))
for mm in range(12):
    for kk in range(Nlev):
        s=Sal1[mm,kk]
        t=Temp[mm,kk]
        p=vlev[k]
        RHO[mm,kk]=dens(s, t, p)
dump_gotm_monthly_clim_file(RHO,ymin,ymax,vlev,'RHO_insitu',month_list,True,dir_gotm_clim_txt)

# Variables with unit conversion
var_list=['PO41','O2(1)', 'Alk','Si1','POC']
for var in var_list:
    print("processing var : ", var)
#   indata_scaled = indata/1000. #1/Liter --> 1/m3
    indata=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
    indata_scaled = indata * RHO/1000.
    dump_gotm_monthly_clim_file(indata_scaled,ymin,ymax,vlev,var,month_list,bottom_fill[var],dir_gotm_clim_txt)

var_list=['CO2']
for var in var_list:
    print("processing var : ", var)
#   indata_scaled = indata/1000. #1/Liter --> 1/m3
    indata=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
    indata_scaled = indata * RHO/1000. *12.0
    dump_gotm_monthly_clim_file(indata_scaled,ymin,ymax,vlev,var,month_list,bottom_fill[var],dir_gotm_clim_txt)

var_list=['PON']
for var in var_list:
    print("processing var : ", var)
#   indata_scaled = indata/1000. #1/Liter --> 1/m3
    indata=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
    indata_scaled = indata * RHO/ 1000. / 14.0
    dump_gotm_monthly_clim_file(indata_scaled,ymin,ymax,vlev,var,month_list,False,dir_gotm_clim_txt)

var_list=['POP']
for var in var_list:
    print("processing var : ", var)
#   indata_scaled = indata/1000. #1/Liter --> 1/m3
    indata=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
    indata_scaled = indata * RHO/ 1000.
    dump_gotm_monthly_clim_file(indata_scaled,ymin,ymax,vlev,var,month_list,False,dir_gotm_clim_txt)

############
# nitrites + nitrates requires unit conversion
############

print("processing var : NO2")

NO2=create_monthly_clim(df,'NO21',vlev,delta,ymin,ymax,'',2,detection_limit[var])
indata_scaled = NO2* RHO/1000.
dump_gotm_monthly_clim_file(indata_scaled,ymin,ymax,vlev,'NO2',month_list,True,dir_gotm_clim_txt)

print("processing var : NO2+NO3")

NO3=create_monthly_clim(df,'NO31',vlev,delta,ymin,ymax,'',2,detection_limit[var])
indata_scaled = NO3* RHO/1000.
dump_gotm_monthly_clim_file(indata_scaled,ymin,ymax,vlev,'NO3',month_list,True,dir_gotm_clim_txt)

############
# Dissolved organic matter
############

print("processing var : DOC as TOC - POC")
# TDP it is expressed in nmol/kg
var="TOC"
TOC=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
var="POC"
POC=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
indata_scaled = (TOC*12.-POC) * RHO/1000.
dump_gotm_monthly_clim_file(indata_scaled,ymin,ymax,vlev,'DOC',month_list,True,dir_gotm_clim_txt)

print("processing var : DON as TN - PON - NO3")
# TDP it is expressed in nmol/kg
var="TN"
TN=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
var="PON"
PON=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
var="NO31"
NO3=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
indata_scaled = (TN-PON/14.-NO3) * RHO/1000.
indata_scaled[indata_scaled<0] = np.nan
dump_gotm_monthly_clim_file(indata_scaled,ymin,ymax,vlev,'DON',month_list,False,dir_gotm_clim_txt)

print("processing var : DOP")
# TDP it is expressed in nmol/kg
var="PO41"
PO4=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
var="TDP"
TDP=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
indata_scaled = (TDP/1000.-PO4) * RHO/1000.
indata_scaled[indata_scaled<0] = np.nan
dump_gotm_monthly_clim_file(indata_scaled,ymin,ymax,vlev,'DOP',month_list,False,dir_gotm_clim_txt)

print("processing var : TP")
# TDP it is expressed in nmol/kg
var="TDP"
TDP=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
var="POP"
POP=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2,detection_limit[var])
indata_scaled = (TDP/1000.+POP) * RHO/1000.
indata_scaled[indata_scaled<0] = np.nan
dump_gotm_monthly_clim_file(indata_scaled,ymin,ymax,vlev,'TP',month_list,True,dir_gotm_clim_txt)


############
### Chlorophyll
############
df1 = pd.read_csv("DATA_BATS/bats_pigments.txt", sep="\t",skiprows = 51, engine='python')

#ordering data for ascending date and ascending depth
# yyyymmdd
# Depth positive downward

df = df1.sort_values(['yyyymmdd', 'Depth'], ascending=[True, True])

print("processing var : chl")
month_list=['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
            'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

Chl=create_monthly_clim(df,'Chl',vlev,delta,ymin,ymax,'',2,detection_limit[var])
indata_scaled = Chl*RHO/1000.
dump_gotm_monthly_clim_file(indata_scaled,ymin,ymax,vlev,'Chl',month_list,False,dir_gotm_clim_txt)


