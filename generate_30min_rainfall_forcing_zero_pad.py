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

    tmp = rain.copy()

    time, nrows, ncols = rain.shape
    __, lat, lon = rain.shape
    time = (time * 6)
    out = np.zeros((time, nrows, ncols))

    # testing
    #nrows = 5
    #ncols = 5

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

    dates = pd.date_range(start='1/1/%s 00:00:00' % (str(year)),
                          periods=time,
                          freq="30min")

    ds_out = xr.Dataset(coords={'lon': lon, 'lat': lat, 'time': dates})
    ds_out['lat'] = rain['lat']
    ds_out['lon'] = rain['lon']
    ds_out['time'] = dates
    ds_out['Rainf'] = xr.DataArray(out, dims=['time', 'lat', 'lon'])
    ds_out.attrs['units'] = 'kg m-2 s-1'
    ds_out.attrs['standard_name'] = "rainfall_flux"
    ds_out.attrs['long_name'] = "Rainfall rate"
    ds_out.attrs['_fillvalue'] = -999.0
    ds_out.attrs['alma_name'] = "Rainf"

    ofname = "awap_30min_rain_zero_pad/AWAP.Rainf.3hr.%d.nc" % (year)
    ds_out.to_netcdf(ofname)

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
    #years = np.arange(1995, 2010+1)

    years = np.arange(1995, 1995+1)

    for year in years:
        main(fpath, year)
    """
