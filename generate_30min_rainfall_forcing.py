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

    fname = "%s/AWAP.Rainf.3hr.%d.nc" % (fpath, year)
    ds = xr.open_dataset(fname)
    rain = ds.Rainf

    # Repeat rainfall data and then divide by increased number of timesteps so
    # to maintain the same rainfall
    new_rain = np.repeat(rain, 6, axis=0)
    new_rain /= 6.0

    # Generate new time sequence
    dates = pd.date_range(start='1/1/%s 00:00:00' % (str(year)),
                          periods=len(new_rain),
                          freq="30min")

    # Create new 30 min rainfall data
    new_rain['time'] = dates
    ofname = "awap_30min_rain/AWAP.Rainf.3hr.%d.nc" % (year)
    new_rain.to_netcdf(ofname)

if __name__ == "__main__":

    """
    # Expecting var to be supplied on cmd line, e.g.
    # $ python generate_30min_rainfall_forcing.py 1995
    if len(sys.argv) < 2:
        raise TypeError("Expecting year name to be supplied on cmd line!")

    year = int(sys.argv[1])
    """

    fpath = "/srv/ccrc/data25/z5218916/data/AWAP_to_netcdf/Rainf"

    #years = np.arange(1995, 2010+1)
    years = np.arange(1996, 2010+1)
    for year in years:
        main(fpath, year)
