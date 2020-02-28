#!/usr/bin/env python
"""
Input forcing for CABLE is 3 hrly, generate 30 min rainfall inputs
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (11.09.2019)"
__email__ = "mdekauwe@gmail.com"

import os
import xarray as xr
import numpy as np
import sys
import glob
import subprocess
import pandas as pd

def main(fpath, year):

    print(year)

    fname = "%s/AWAP.Rainf.3hr.%d.nc" % (fpath, year)
    ds = xr.open_dataset(fname, chunks={'time':1})
    #ds = xr.open_dataset(fname)
    rain = ds.Rainf
    __, lat, lon = rain.shape

    # Create a DataArray with the new times
    ntime = rain.sizes['time']*6 # 3hourly to 30 min.
    dates = xr.DataArray(pd.date_range(start=f'1/1/{year} 00:00:00',
                         periods=ntime,freq="30min"),dims=['time'])

    #rain_test = rain.broadcast_like(dates)
    #rain_test = rain_test.fillna(0.0)
    rain = rain.fillna(-1.0) #Precip shouldn't be negative
    rain_test = rain.broadcast_like(dates).fillna(0.0)
    rain_test = rain_test.where(rain_test > -1.0, -999.)

    enc = {'lat':{'_FillValue':False},
           'lon':{'_FillValue':False},
           'Rainf':{'_FillValue':False}}

    ofname = "awap_30min_rain_zero_pad/AWAP.Rainf.3hr.%d.nc" % (year)

    rain_test.to_netcdf(ofname, encoding=enc)

if __name__ == "__main__":

    """
    Run like this...

    nohup ./generate_30min_rainfall_forcing.py 1995 1997 &
    nohup ./generate_30min_rainfall_forcing.py 1998 2000 &
    nohup ./generate_30min_rainfall_forcing.py 2001 2003 &
    nohup ./generate_30min_rainfall_forcing.py 2004 2006 &
    nohup ./generate_30min_rainfall_forcing.py 2007 2010 &
    """

    # Expecting var to be supplied on cmd line, e.g.
    # $ python generate_30min_rainfall_forcing_zero_pad.py 1995
    if len(sys.argv) < 2:
        raise TypeError("Expecting year name to be supplied on cmd line!")

    st_year = int(sys.argv[1])
    en_year = int(sys.argv[2])

    #fpath = "/srv/ccrc/data25/z5218916/data/AWAP_to_netcdf/Rainf"
    fpath = "../"

    #main(fpath, year)

    #"""
    #years = np.arange(1995, 2010+1)
    years = np.arange(st_year, en_year+1)

    for year in years:
        main(fpath, year)
    #"""
