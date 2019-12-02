#!/usr/bin/env python
"""
Input forcing for CABLE is 3 hrly, generate 30 min rainfall inputs. Here we're
generating a long timeseries (x6) and filling new gaps with zeros, so that we
have no change in rainfall timing or amount
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (02.12.2019)"
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

    # Generate output rain field that is six times as long and pad new timesteps
    # with zeros, i.e. go from 3 hourly to 30 min rainfall data with no change
    # in timing of rainfall or amount.
    time, nrows, ncols = rain.shape
    __, lat, lon = rain.shape
    time = (time * 6)
    out = np.zeros((time, nrows, ncols), dtype=np.float32)

    # testing
    #nrows = 5
    #ncols = 5

    for r in range(nrows):
        #print(r,nrows)
        for c in range(ncols):
            vals = rain[:,r,c].values
            six_count = 0
            cnt = 0

            # Fill all time slices with missing value, otherwise values
            # would have been changed to zero
            if np.all(vals < -500.0):
                out[:,r,c] = -999.0

            for t in range(time):
                if six_count == 6:
                    print(t, six_count, cnt)
                    out[t,r,c] = vals[cnt]
                    cnt += 1
                    six_count = 0
                six_count += 1

    dates = pd.date_range(start='1/1/%s 00:00:00' % (str(year)),
                          periods=time,
                          freq="30min")

    ds_out = xr.Dataset(coords={'lon': lon, 'lat': lat, 'time': dates})

    lats = rain['lat'].values.astype(np.float64)
    ds_out['lat'] = xr.DataArray(lats, dims=['lat'])

    lons = rain['lon'].values.astype(np.float64)
    ds_out['lon'] = xr.DataArray(lons, dims=['lon'])

    ds_out['time'] = dates

    ds_out['Rainf'] = xr.DataArray(out, dims=['time', 'lat', 'lon'])
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

    ds_out.lat.encoding['_FillValue'] = False
    ds_out.lon.encoding['_FillValue'] = False
    ds_out.Rainf.encoding['_FillValue'] = False
    ds_out['Rainf'].attrs['_fillvalue'] = -999.0
    ds_out.to_netcdf("test.nc")

    ofname = "awap_30min_rain_zero_pad/AWAP.Rainf.3hr.%d.nc" % (year)
    ds_out.to_netcdf(ofname)

if __name__ == "__main__":

    """
    Run like this...

    nohup ./generate_30min_rainfall_forcing_zero_pad.py 1995 1997 &
    nohup ./generate_30min_rainfall_forcing_zero_pad.py 1998 2000 &
    nohup ./generate_30min_rainfall_forcing_zero_pad.py 2001 2003 &
    nohup ./generate_30min_rainfall_forcing_zero_pad.py 2004 2006 &
    nohup ./generate_30min_rainfall_forcing_zero_pad.py 2007 2010 &
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
