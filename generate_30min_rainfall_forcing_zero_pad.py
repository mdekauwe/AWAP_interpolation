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
    ds = xr.open_dataset(fname)
    rain = ds.Rainf

    time, nrows, ncols = rain.shape
    time = (time * 6)
    out = np.zeros((time, nrows, ncols))

    for r in range(nrows):
        print(r,nrows)
        for c in range(ncols):
            vals = rain[:,r,c].values
            six_count = 0
            cnt = 0

            if np.any(vals < -500.0):
                out[:,r,c] = -999.0
            else:
                out[:,r,c] = 0.0

            for t in range(time):
                if six_count == 6:
                    out[t,r,c] = vals[cnt]
                    cnt += 1
                    six_count = 0
                six_count += 1


    # Repeat rainfall data and then divide by increased number of timesteps so
    # to maintain the same rainfall total, but spread over 48 time slots. This
    # will mean smaller, more frequent events though
    new_rain = np.repeat(rain, 6, axis=0)

    # Generate new time sequence
    dates = pd.date_range(start='1/1/%s 00:00:00' % (str(year)),
                          periods=len(new_rain),
                          freq="30min")


    # Create new 30 min rainfall data
    new_rain['time'] = dates

    new_rain['Rainf'] = out

    new_rain.attrs['units'] = 'kg m-2 s-1'
    new_rain.attrs['standard_name'] = "rainfall_flux"
    new_rain.attrs['long_name'] = "Rainfall rate"

    ofname = "awap_30min_rain/AWAP.Rainf.3hr.%d.nc" % (year)
    new_rain.to_netcdf(ofname)

if __name__ == "__main__":

    #"""
    # Expecting var to be supplied on cmd line, e.g.
    # $ python generate_30min_rainfall_forcing.py 1995
    if len(sys.argv) < 2:
        raise TypeError("Expecting year name to be supplied on cmd line!")

    year = int(sys.argv[1])
    #"""

    fpath = "/srv/ccrc/data25/z5218916/data/AWAP_to_netcdf/Rainf"
    #fpath = "../"

    main(fpath, year)

    """
    years = np.arange(1995, 2010+1)

    for year in years:
        main(fpath, year)
    """
