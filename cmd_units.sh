ncatted -a units,'Rainf',c,c,'kg m-2 s-1' AWAP.Rainf.3hr.1995.nc

for f in *.nc;
do
    ncatted -a units,'Rainf',c,c,'kg m-2 s-1' $f
done
