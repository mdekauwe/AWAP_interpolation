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
    __, lat, lon = rain.shape

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

    mask = np.full(new_rain.shape, True)
    mask[::6, :, :] = False
    new_rain = np.where(mask == True, 0., new_rain)

    ds_out = xr.Dataset(coords={'lon': lon, 'lat': lat, 'time': dates})

    lats = rain['lat'].values.astype(np.float64)
    ds_out['lat'] = xr.DataArray(lats, dims=['lat'])

    lons = rain['lon'].values.astype(np.float64)
    ds_out['lon'] = xr.DataArray(lons, dims=['lon'])

    ds_out['time'] = dates

    ds_out['Rainf'] = xr.DataArray(new_rain, dims=['time', 'lat', 'lon'])
    ds_out['Rainf'].attrs['units'] = 'kg m-2 s-1'
    ds_out['Rainf'].attrs['standard_name'] = "rainfall_flux"
    ds_out['Rainf'].attrs['long_name'] = "Rainfall rate"

    ds_out['Rainf'].attrs['alma_name'] = "Rainf"

    ds_out['time'].attrs['long_name'] = 'Time'
    ds_out['time'].attrs['standard_name'] = "time"

    ds_out['lon'].attrs['long_name'] = 'Longitude'
    ds_out['lon'].attrs['standard_name'] = "longitude"
    ds_out['lon'].attrs['axis'] = "X"
    ds_out['lon'].attrs['units'] = "degrees_east"

    ds_out['lat'].attrs['long_name'] = 'Latitude'
    ds_out['lat'].attrs['standard_name'] = "latitude"
    ds_out['lat'].attrs['axis'] = "Y"
    ds_out['lat'].attrs['units'] = "degrees_north"

    ds_out['time'].attrs['axis'] = 'T'
    ds_out['time'].attrs['units'] = "hours since 1995-01-01 00:00:00" ;

    ds_out.lat.encoding['_FillValue'] = False
    ds_out.lon.encoding['_FillValue'] = False
    ds_out.Rainf.encoding['_FillValue'] = False
    ds_out['Rainf'].attrs['_fillvalue'] = -999.0

    ofname = "awap_30min_rain_zero_pad/AWAP.Rainf.3hr.%d.nc" % (year)
    ds_out.to_netcdf(ofname, unlimited_dims='time')


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

    fpath = "/srv/ccrc/data25/z5218916/data/AWAP_to_netcdf/Rainf"
    #fpath = "../"

    #main(fpath, year)

    #"""
    #years = np.arange(1995, 2010+1)
    years = np.arange(st_year, en_year+1)

    for year in years:
        main(fpath, year)
    #"""
