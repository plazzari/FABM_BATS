import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from auxiliary import *

# Constants.
a = [0.0080, -0.1692, 25.3851, 14.0941, -7.0261, 2.7081]
b = [0.0005, -0.0056, -0.0066, -0.0375, 0.0636, -0.0144]
c = [0.6766097, 2.00564e-2, 1.104259e-4, -6.9698e-7, 1.0031e-9]
d = [3.426e-2, 4.464e-4, 4.215e-1, -3.107e-3]
e = [2.070e-5, -6.370e-10, 3.989e-15]
k = 0.0162

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

def create_monthly_clim(df,var,vlev,delta,ymin,ymax,conversion_var,mode,det_limit):
    Nrows=df.shape[0]
    Nk=len(vlev)
    clim=np.zeros((12,Nk))
    conversion_factor=np.zeros((12,Nk)) + 1.0

    bins_limit=np.zeros(Nk+1)

    bins_limit[0]=0. 
    for k in range(1,Nk):
        bins_limit[k] = 0.5*(vlev[k-1]+vlev[k])
    bins_limit[Nk] = 0.5*(vlev[Nk-1]+12000.)


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


#           rule2 = dfclim['Depth'] >  lev-delta[k]
#           rule3 = dfclim['Depth'] <= lev+delta[k]
#           rule2 = dfclim['Depth'] >  bins_limit[k]
#           rule3 = dfclim['Depth'] <= bins_limit[k+1]
            rule4 = dfclim['yyyymmdd'] > 0
#          
            rule1 = dfclim[var] > -998.0 
            df1 = dfclim.loc[rule1]
            rule2 = df1['Depth'] >  bins_limit[k]
            df2 = df1.loc[rule2]
            rule3 = df2['Depth'] <= bins_limit[k+1]
            df3 = df2.loc[rule3]
            rule4 = df3['yyyymmdd'] > 0
            df4 = df3.loc[rule4]

            if not np.isnan(det_limit):
               sample_filtered=np.maximum(df4[var].values,det_limit/2.0)
            else:
               sample_filtered=df4[var].values

            if (sample_filtered.size == 0) or (sum(np.isnan(sample_filtered)) == sample_filtered.size):
                clim[tt,k]=np.nan
                print(["var "   + var])
                print(["month " + str(mm)])
                print(["lev "   + str(lev)])
                print(["# 0 "])
                print(["++++++++++++++++++++++++++++++++++++++"])
            else:
                clim[tt,k]=np.nanpercentile(sample_filtered,50.0)
                print([ "var " + var])
                print(["month " + str(mm)])
                print([ "lev " + str(lev)])
                print([ "#   " + str( sample_filtered.size - sum(np.isnan(sample_filtered))) ])
                print([ "val " + str(clim[tt,k])])
                print(["++++++++++++++++++++++++++++++++++++++"])

    if mode == 0:
        return df4
    if mode == 1:
        return conversion_factor
    if mode == 2:
        return clim
def dump_gotm_monthly_clim_file(indata,ymin,ymax,lev,var,month_list,bottom_value, dir_output=''):

    nrows=len(lev)

    file_gotm = dir_output + '/' + var + '_clim.txt'

    fid = open(file_gotm,'w')

    yyyy=int((ymax+ymin)/2)

# days per month 
#        [31,28,31,30,31,30,31,31,30,31,30,31]
    dd  =[16,15,16,16,16,16,16,16,16,16,16,16]
    HH  =[12,0 ,12, 0,12, 0,12,12, 0,12, 0,12]

    month_dict={'JAN':0,
                'FEB':1,
                'MAR':2, 
                'APR':3, 
                'MAY':4,
                'JUN':5,
                'JUL':6,
                'AUG':7,
                'SEP':8,
                'OCT':9,
                'NOV':10,
                'DEC':11}

    for month in month_list:

        tt=month_dict[month]

        mm = tt +1
        count = 1 # Start from 1 since we add -10000 m value

        for zz,d in enumerate(lev):
            if not np.isnan(indata[tt,zz]):
                count += 1

# Write output file
        current_date=datetime.datetime(yyyy, mm, dd[tt], HH[tt], 0, 0)
        gotm_header= current_date.strftime("%Y-%m-%d %H:%M:%S\t" + str(count) + "\t2")
        fid.write(gotm_header)
        fid.write("\n")
        last_value=0.
        for zz,d in enumerate(lev): 
            if not np.isnan(indata[tt,zz]):
               fid.write(str(-d))
               fid.write("\t")
               fid.write(str(indata[tt,zz]))
               fid.write("\n")
               last_value=indata[tt,zz]
        if bottom_value:
           fid.write(str(- 12000.)) #  The Mariana Trench depth
           fid.write("\t")
           fid.write(str(last_value))
           fid.write("\n")
        else:
           fid.write(str(- 12000.)) #  The Mariana Trench depth
           fid.write("\t")
           fid.write(str(0.0))
           fid.write("\n")

    fid.close()

def dens0(s, t):
    """
    Density of Sea Water at atmospheric pressure.

    Parameters
    ----------
    s(p=0) : array_like
             salinity [psu (PSS-78)]
    t(p=0) : array_like
             temperature [℃ (ITS-90)]

    Returns
    -------
    dens0(s, t) : array_like
                  density  [kg m :sup:`3`] of salt water with properties
                  (s, t, p=0) 0 db gauge pressure

    Examples
    --------
    >>> # Data from UNESCO Tech. Paper in Marine Sci. No. 44, p22
    >>> import seawater as sw
    >>> from seawater.library import T90conv
    >>> s = [0, 0, 0, 0, 35, 35, 35, 35]
    >>> t = T90conv([0, 0, 30, 30, 0, 0, 30, 30])
    >>> sw.dens0(s, t)
    array([  999.842594  ,   999.842594  ,   995.65113374,   995.65113374,
            1028.10633141,  1028.10633141,  1021.72863949,  1021.72863949])

    References
    ----------
    .. [1] Fofonoff, P. and Millard, R.C. Jr UNESCO 1983. Algorithms for
       computation of fundamental properties of seawater. UNESCO Tech. Pap. in
       Mar. Sci., No. 44, 53 pp.  Eqn.(31) p.39.
       http://unesdoc.unesco.org/images/0005/000598/059832eb.pdf

    .. [2] Millero, F.J. and  Poisson, A. International one-atmosphere
       equation of state of seawater. Deep-Sea Res. 1981. Vol28A(6) pp625-629.
       doi:10.1016/0198-0149(81)90122-9

    """

    s, t = list(map(np.asanyarray, (s, t)))

    T68 = T68conv(t)

    # UNESCO 1983 Eqn.(13) p17.
    b = (8.24493e-1, -4.0899e-3, 7.6438e-5, -8.2467e-7, 5.3875e-9)
    c = (-5.72466e-3, 1.0227e-4, -1.6546e-6)
    d = 4.8314e-4
    return (smow(t) + (b[0] + (b[1] + (b[2] + (b[3] + b[4] * T68) * T68) *
            T68) * T68) * s + (c[0] + (c[1] + c[2] * T68) * T68) * s *
            s ** 0.5 + d * s ** 2)

def dens(s, t, p):
    """
    Density of Sea Water using UNESCO 1983 (EOS 80) polynomial.

    Parameters
    ----------
    s(p) : array_like
           salinity [psu (PSS-78)]
    t(p) : array_like
           temperature [℃ (ITS-90)]
    p : array_like
        pressure [db].

    Returns
    -------
    dens : array_like
           density  [kg m :sup:`3`]

    Examples
    --------
    >>> # Data from Unesco Tech. Paper in Marine Sci. No. 44, p22.
    >>> import seawater as sw
    >>> from seawater.library import T90conv
    >>> s = [0, 0, 0, 0, 35, 35, 35, 35]
    >>> t = T90conv([0, 0, 30, 30, 0, 0, 30, 30])
    >>> p = [0, 10000, 0, 10000, 0, 10000, 0, 10000]
    >>> sw.dens(s, t, p)
    array([  999.842594  ,  1045.33710972,   995.65113374,  1036.03148891,
            1028.10633141,  1070.95838408,  1021.72863949,  1060.55058771])

    References
    ----------
    .. [1] Fofonoff, P. and Millard, R.C. Jr UNESCO 1983. Algorithms for
       computation of fundamental properties of seawater. UNESCO Tech. Pap. in
       Mar. Sci., No. 44, 53 pp.  Eqn.(31) p.39.
       http://unesdoc.unesco.org/images/0005/000598/059832eb.pdf

    .. [2] Millero, F.J., Chen, C.T., Bradshaw, A., and Schleicher, K. A new
       high pressure equation of state for seawater. Deap-Sea Research., 1980,
       Vol27A, pp255-264. doi:10.1016/0198-0149(80)90016-3

    """

    s, t, p = list(map(np.asanyarray, (s, t, p)))

    # UNESCO 1983. Eqn..7  p.15.
    densP0 = dens0(s, t)
    K = seck(s, t, p)
    p = p / 10.  # Convert from db to atm pressure units.
    return densP0 / (1 - p / K)
def seck(s, t, p=0):
    """
    Secant Bulk Modulus (K) of Sea Water using Equation of state 1980.
    UNESCO polynomial implementation.

    Parameters
    ----------
    s(p) : array_like
           salinity [psu (PSS-78)]
    t(p) : array_like
           temperature [℃ (ITS-90)]
    p : array_like
        pressure [db].

    Returns
    -------
    k : array_like
        secant bulk modulus [bars]

    Examples
    --------
    >>> # Data from Unesco Tech. Paper in Marine Sci. No. 44, p22.
    >>> import seawater as sw
    >>> s = [0, 0, 0, 0, 35, 35, 35, 35]
    >>> t = T90conv([0, 0, 30, 30, 0, 0, 30, 30])
    >>> p = [0, 10000, 0, 10000, 0, 10000, 0, 10000]
    >>> sw.seck(s, t, p)
    array([ 19652.21      ,  22977.2115    ,  22336.0044572 ,  25656.8196222 ,
            21582.27006823,  24991.99729129,  23924.21823158,  27318.32472464])

    References
    ----------
    .. [1] Fofonoff, P. and Millard, R.C. Jr UNESCO 1983. Algorithms for
       computation of fundamental properties of seawater. UNESCO Tech. Pap. in
       Mar. Sci., No. 44, 53 pp.  Eqn.(31) p.39.
       http://unesdoc.unesco.org/images/0005/000598/059832eb.pdf

    .. [2] Millero, F.J. and  Poisson, A. International one-atmosphere equation
       of state of seawater. Deep-Sea Res. 1981. Vol28A(6) pp625-629.
       doi:10.1016/0198-0149(81)90122-9

    """
    s, t, p = list(map(np.asanyarray, (s, t, p)))

    # Compute compression terms.
    p = p / 10.0  # Convert from db to atmospheric pressure units.
    T68 = T68conv(t)

    # Pure water terms of the secant bulk modulus at atmos pressure.
    # UNESCO Eqn 19 p 18.
    # h0 = -0.1194975
    h = [3.239908, 1.43713e-3, 1.16092e-4, -5.77905e-7]
    AW = h[0] + (h[1] + (h[2] + h[3] * T68) * T68) * T68

    # k0 = 3.47718e-5
    k = [8.50935e-5, -6.12293e-6, 5.2787e-8]
    BW = k[0] + (k[1] + k[2] * T68) * T68

    # e0 = -1930.06
    e = [19652.21, 148.4206, -2.327105, 1.360477e-2, -5.155288e-5]
    KW = e[0] + (e[1] + (e[2] + (e[3] + e[4] * T68) * T68) * T68) * T68

    # Sea water terms of secant bulk modulus at atmos. pressure.
    j0 = 1.91075e-4
    i = [2.2838e-3, -1.0981e-5, -1.6078e-6]
    A = AW + (i[0] + (i[1] + i[2] * T68) * T68 + j0 * s ** 0.5) * s

    m = [-9.9348e-7, 2.0816e-8, 9.1697e-10]
    B = BW + (m[0] + (m[1] + m[2] * T68) * T68) * s  # Eqn 18.

    f = [54.6746, -0.603459, 1.09987e-2, -6.1670e-5]
    g = [7.944e-2, 1.6483e-2, -5.3009e-4]
    K0 = (KW + (f[0] + (f[1] + (f[2] + f[3] * T68) * T68) * T68 +
                (g[0] + (g[1] + g[2] * T68) * T68) * s ** 0.5) * s)  # Eqn 16.
    return K0 + (A + B * p) * p  # Eqn 15.

def T68conv(T90):
    """
    Convert ITS-90 temperature to IPTS-68

    :math:`T68  = T90 * 1.00024`

    Parameters
    ----------
    t : array_like
           temperature [℃ (ITS-90)]

    Returns
    -------
    t : array_like
           temperature [℃ (IPTS-68)]

    Notes
    -----
    The International Practical Temperature Scale of 1968 (IPTS-68) need to be
    correct to the ITS-90. This linear transformation is accurate within
    0.5 ℃ for conversion between IPTS-68 and ITS-90 over the
    oceanographic temperature range.

    Examples
    --------
    >>> import seawater as sw
    >>> T68conv(19.995201151723585)
    20.0

    References
    ----------
    .. [1] Saunders, P. M., 1991: The International Temperature Scale of 1990,
       ITS-90. WOCE Newsletter, No. 10, WOCE International Project Office,
       Southampton, United Kingdom, 10.

    """
    T90 = np.asanyarray(T90)
    return T90 * 1.00024
def smow(t):
    """
    Density of Standard Mean Ocean Water (Pure Water) using EOS 1980.

    Parameters
    ----------
    t : array_like
        temperature [℃ (ITS-90)]

    Returns
    -------
    dens(t) : array_like
              density  [kg m :sup:`3`]

    Examples
    --------
    >>> # Data from UNESCO Tech. Paper in Marine Sci. No. 44, p22.
    >>> import seawater as sw
    >>> t = T90conv([0, 0, 30, 30, 0, 0, 30, 30])
    >>> sw.smow(t)
    array([ 999.842594  ,  999.842594  ,  995.65113374,  995.65113374,
            999.842594  ,  999.842594  ,  995.65113374,  995.65113374])

    References
    ----------
    .. [1] Fofonoff, P. and Millard, R.C. Jr UNESCO 1983. Algorithms for
       computation of fundamental properties of seawater. UNESCO Tech. Pap. in
       Mar. Sci., No. 44, 53 pp.  Eqn.(31) p.39.
       http://unesdoc.unesco.org/images/0005/000598/059832eb.pdf

    .. [2] Millero, F.J. and  Poisson, A. International one-atmosphere equation
       of state of seawater. Deep-Sea Res. 1981. Vol28A(6) pp625-629.
       doi:10.1016/0198-0149(81)90122-9

    """
    t = np.asanyarray(t)

    a = (999.842594, 6.793952e-2, -9.095290e-3, 1.001685e-4, -1.120083e-6,
         6.536332e-9)

    T68 = T68conv(t)
    return (a[0] + (a[1] + (a[2] + (a[3] + (a[4] + a[5] * T68) * T68) * T68) *
            T68) * T68)
