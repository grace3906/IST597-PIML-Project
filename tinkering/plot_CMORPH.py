import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime

# Start and end dates
time2plt = datetime(2018, 2, 3, 2, 0)

CMROOT = '/glade/work/jpan/CMORPH/www.ncei.noaa.gov/data/cmorph-high-resolution-global-precipitation-estimates/access/30min/8km/'
FILSTR = 'CMORPH_V1.0_ADJ_8km-30min_%s.nc'
pvar = 'cmorph'
OUTPT = os.path.join(CMROOT, 'cmorph_vec_201812.nc')

SLICE = slice(None, None, 2)


folder = os.path.join(CMROOT, str(time2plt.year), time2plt.strftime('%m'), time2plt.strftime('%d'))
filefill = time2plt.strftime('%Y%m%d%H')

ds = xr.open_dataset(os.path.join(folder, FILSTR % filefill))
ds = ds.sel(lon=ds.lon.sel(lon=slice(230, 310))[SLICE], lat=ds.lat.sel(lat=slice(10, 60))[SLICE], time=time2plt)
plt.contourf(ds.lon, ds.lat, ds.cmorph.values)
plt.show()
