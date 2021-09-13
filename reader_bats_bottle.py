import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from auxiliary import *

def crdir(dirName):
    # Create directory
    try:
        # Create target Directory
        os.mkdir(dirName)
        print("Directory " , dirName ,  " Created ")
    except FileExistsError:
        print("Directory " , dirName ,  " already exists")

def samp_date_hist(df,myvar='yyyymmdd',dir_output=''):

    yyyy=[]
    mm=[]
    dd=[]

    for yyyymmdd,var in zip(df['yyyymmdd'].values,df[myvar].values):
        if(float(var) > -998.):
            yyyy.append(int(str(yyyymmdd)[0:4]))
            mm.append(  int(str(yyyymmdd)[4:6]))
            dd.append(  int(str(yyyymmdd)[6:8]))

    print(set(yyyy))
    print(set(mm))
    print(set(dd))
    fig,axs=plt.subplots(2,1)
    fig.set_size_inches(10,10)
 
#   Annual year frequency histogram
    ax=axs[0]
    ax.hist(yyyy)
    ax.set_xlabel('years')
    ax.set_ylabel('N of samples')

    ax=axs[1]
    x=np.arange(1,13)
    bins_edges=np.arange(0.5,13.5,1.0)
    res, bins, patches=ax.hist(mm,bins=bins_edges,rwidth=0.5)
    ax.set_xlabel('months')
    ax.set_ylabel('N of samples')
    ax.set_xticks(range(1,13))
    ax.set_xticklabels(('J','F','M','A','M','J','J','A','S','O','N','D'))

    fileout=dir_output + '/' + 'hyst_time_samples_' + myvar + '.png'
    fig.savefig(fileout, format='png',dpi=150)

def samp_depth_hist(df,myvar='yyyymmdd',dir_output=''):

    depth=[]
    depth0_200=[]
    depth0_500=[]
    n_bins=100

    for d,var in zip(df['Depth'].values,df[myvar].values):
        if(float(var) > -998.):
            depth.append(d)
            if(d < 200.):
                depth0_200.append(d)
            if(d < 500.):
                depth0_500.append(d)

    fig,axs=plt.subplots(3,1)
    fig.set_size_inches(10,14)

    ax=axs[0]
    ax.hist(depth,bins=n_bins)
    dd = np.arange(0.,4000.,500.)
    ax.set_xticks(dd)
    ax.grid(linestyle="--", linewidth=0.5, color='.25', zorder=-10)
    ax.set_xlabel('Depth [m]')
    ax.set_ylabel('N of samples')
    ax.set_title('Surface to bottom')
    ax=axs[1]
    ax.hist(depth0_500,bins=n_bins)
    dd = np.arange(0.,500.,50.)
    ax.set_xticks(dd)
    ax.grid(linestyle="--", linewidth=0.5, color='.25', zorder=-10)
    ax.set_xlabel('Depth [m]')
    ax.set_ylabel('N of samples')
    ax.set_title('Surface to 500 m depth')
    ax=axs[2]
    ax.hist(depth0_200,bins=n_bins)
    dd = np.arange(0.,200.,10.)
    ax.set_xticks(dd)
    ax.grid(linestyle="--", linewidth=0.5, color='.25', zorder=-10)
    ax.set_xlabel('Depth [m]')
    ax.set_ylabel('N of samples')
    ax.set_title('Surface to 200 m depth')
    fig.suptitle(myvar)

    fileout=dir_output + '/' + 'hyst_depth_samples_' + myvar + '.png'
    fig.savefig(fileout, format='png',dpi=150)

def dump_gotm_file(dfin,var,dir_output=''):

    file_gotm = dir_output + '/' + var + '.txt'

    fid = open(file_gotm,'w')

    yyyymmdd=df['yyyymmdd'].unique()

    for mytime in yyyymmdd:

            yyyy=int(str(mytime)[0:4])
            mm  =int(str(mytime)[4:6])
            dd  =int(str(mytime)[6:8])

            data=df.loc[df['yyyymmdd'] == mytime]
            time=data['time'].unique()

            for hhmm in time:

                HH=int(str(hhmm).zfill(4)[0:2])
                MM=int(str(hhmm).zfill(4)[2:4])
                profile=data.loc[(data['time'] == hhmm) & (data[var] > -998.0)]
                nrows  =profile.shape[0]
                if nrows > 0:
# Write output file
                    current_date=datetime.datetime(yyyy, mm, dd, HH, MM, 0)
                    gotm_header= current_date.strftime("%Y-%m-%d %H:%M:%S\t" + str(nrows) + "\t2")
                    fid.write(gotm_header)
                    fid.write("\n")
                    for d,val in zip(profile['Depth'].values,profile[var].values):
                        fid.write(str(-d))
                        fid.write("\t")
                        fid.write(str(val))
                        fid.write("\n")

    fid.close()

def create_monthly_clim(df,var,vlev,delta,ymin,ymax,conversion_var,mode):
    Nrows=df.shape[0]
    Nk=len(vlev)
    clim=np.zeros((12,Nk))
    conversion_factor=np.zeros((12,Nk)) + 1.0

    for tt in range(0,12):
        mm = tt + 1
        time_filter_idx=[]
        for index, row in df.iterrows():
            yyyymmdd=row['yyyymmdd']
            yyyy=int(str(int(yyyymmdd))[0:4])
            month=int(str(int(yyyymmdd))[4:6])
#           print(month)
            if ( month == mm) and ( yyyy > ymin) and ( yyyy < ymax):
                time_filter_idx.append(index)

        dfclim=df.iloc[time_filter_idx,:].copy(deep=True)

        for k,lev in enumerate(vlev):

            if conversion_var != '':

                rule1 = dfclim[conversion_var] > -998.0 
                rule2 = dfclim['Depth'] >  lev-delta[k]
                rule3 = dfclim['Depth'] <= lev+delta[k]
                rule4 = dfclim['yyyymmdd'] > 0
#           
                df1 = dfclim.loc[rule1]
                df2 = df1.loc[rule2]
                df3 = df2.loc[rule3]
                df4 = df3.loc[rule4]
                sample_filtered=df4[conversion_var].values
                conversion_factor[tt,k]=np.nanpercentile(sample_filtered,50.0)

            rule1 = dfclim[var] > -998.0 
            rule2 = dfclim['Depth'] >  lev-delta[k]
            rule3 = dfclim['Depth'] <= lev+delta[k]
            rule4 = dfclim['yyyymmdd'] > 0
#          
            df1 = dfclim.loc[rule1]
            df2 = df1.loc[rule2]
            df3 = df2.loc[rule3]
            df4 = df3.loc[rule4]
            sample_filtered=df4[var].values
            clim[tt,k]=np.nanpercentile(sample_filtered,50.0)*conversion_factor[tt,k]

    if mode == 0:
        return df4
    if mode == 1:
        return conversion_factor
    if mode == 2:
        return clim
def dump_gotm_monthly_clim_file(indata,ymin,ymax,lev,var,dir_output=''):

    nrows=len(lev)

    file_gotm = dir_output + '/' + var + '_clim.txt'

    fid = open(file_gotm,'w')

    yyyy=int((ymax+ymin)/2)

# days per month 
#        [31,28,31,30,31,30,31,31,30,31,30,31]
    dd  =[16,15,16,16,16,16,16,16,16,16,16,16]
    HH  =[12,0 ,12, 0,12, 0,12,12, 0,12, 0,12]

    for tt in range(12):
        mm = tt +1
# Write output file
        current_date=datetime.datetime(yyyy, mm, dd[tt], HH[tt], 0, 0)
        gotm_header= current_date.strftime("%Y-%m-%d %H:%M:%S\t" + str(nrows) + "\t2")
        fid.write(gotm_header)
        fid.write("\n")
        for zz,d in enumerate(lev): 
            if not np.isnan(indata[tt,zz]):
               fid.write(str(-d))
               fid.write("\t")
               fid.write(str(indata[tt,zz]))
               fid.write("\n")
        if not np.isnan(indata[tt,zz]):
           fid.write(str(- 10984.0)) #  The Mariana Trench depth
           fid.write("\t")
           fid.write(str(indata[tt,-1]))
           fid.write("\n")
        else:
           fid.write(str(- 10984.0)) #  The Mariana Trench depth
           fid.write("\t")
           fid.write(str(0.0))
           fid.write("\n")

    fid.close()
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
       delta[k]=2. 
    if (vlev[k] > 160.) and (vlev[k] <= 300.):
       delta[k]=5. 
    if (vlev[k] > 300.) and (vlev[k] <= 1400.):
       delta[k]=10. 
    if (vlev[k] > 1400.): 
       delta[k]=20. 

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

#for var in var_list:

#   samp_date_hist(df,var, dirplots)
#   samp_depth_hist(df,var, dirplots)

#    dump_gotm_file(df,var, dir_gotm_txt)


#### Create climatology
ymin=2009
ymax=2020
# Variables with no unit conversion

# Temperature
print("processing var : Temperature")
var='Temp'
Temp=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2)
dump_gotm_monthly_clim_file(Temp,ymin,ymax,vlev,var,dir_gotm_clim_txt)

# Salinity
print("processing var : Salinity")
var='Sal1'
Sal1=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2)
dump_gotm_monthly_clim_file(Sal1,ymin,ymax,vlev,var,dir_gotm_clim_txt)

# Density scaling using in-situ computed density from T and S
print("processing var : RHO")
RHO=np.zeros((12,Nlev))
for mm in range(12):
    for kk in range(Nlev):
        s=Sal1[mm,kk]
        t=Temp[mm,kk]
        p=vlev[k]
        RHO[mm,kk]=dens(s, t, p)
dump_gotm_monthly_clim_file(RHO,ymin,ymax,vlev,'RHO_insitu',dir_gotm_clim_txt)

# Variables with unit conversion
var_list=['PO41','O2(1)','CO2', 'Alk','Si1','POC','PON','POP']
for var in var_list:
    print("processing var : ", var)
#   indata_scaled = indata/1000. #1/Liter --> 1/m3
    indata=create_monthly_clim(df,var,vlev,delta,ymin,ymax,'',2)
    indata_scaled = indata * RHO/1000.
    dump_gotm_monthly_clim_file(indata_scaled,ymin,ymax,vlev,var,dir_gotm_clim_txt)

############
# nitrites + nitrates requires unit conversion
############

print("processing var : NOX")

NO2=create_monthly_clim(df,'NO21',vlev,delta,ymin,ymax,'',2)
NO3=create_monthly_clim(df,'NO31',vlev,delta,ymin,ymax,'',2)
indata_scaled = (NO2+NO3)* RHO/1000.
dump_gotm_monthly_clim_file(indata_scaled,ymin,ymax,vlev,'NOX',dir_gotm_clim_txt)
