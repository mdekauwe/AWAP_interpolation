#!/bin/bash
#PBS -m ae
#PBS -P w35
#PBS -q normal
#PBS -M mdekauwe@gmail.com
#PBS -l mem=128GB
#PBS -l ncpus=1
#PBS -l walltime=03:00:00
#PBS -l wd
#PBS -j oe
#PBS -l storage=gdata/w35+gdata/wd9

module load dot
module add netcdf/4.7.1
source activate sci

#python ./generate_30min_rainfall_forcing.py 1995 2010
python ./generate_30min_rainfall_forcing.py 2003 2010
