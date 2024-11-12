import os
import numpy as np
import xarray as xr
from datetime import datetime, timedelta

# Start and end dates
start = datetime(2018, 1, 1, 0, 0)  # January 1, 2018 at 00:00
end = datetime(2018, 9, 30, 23, 30)  # September 30, 2018 at 23:30
TSTEP = timedelta(minutes=30)

CMROOT = '/glade/work/jpan/CMORPH/www.ncei.noaa.gov/data/cmorph-high-resolution-global-precipitation-estimates/access/30min/8km/'
FILSTR = 'CMORPH_V1.0_ADJ_8km-30min_%s.nc'
pvar = 'cmorph'

SLICE = slice(None, None, 2)

current = start
masks, mastermask = None, None
longr, latgr = None, None
while current <= end:
   folder = os.path.join(CMROOT, str(current.year), current.strftime('%m'), current.strftime('%d'))
   filefill = current.strftime('%Y%m%d%H')
   #print(FILSTR % filefill)

   ds = xr.open_dataset(os.path.join(folder, FILSTR % filefill))
   ds = ds.sel(lon=ds.lon[SLICE], lat=ds.lat[SLICE])

   if current == start:
      mask1 = (ds.lat >= 42) & (ds.lat < 52) & (ds.lon > 230) & (ds.lon < 265)
      mask2 = (ds.lat >= 24) & (ds.lat < 42) & (ds.lon > 230) & (ds.lon < 285)
      mask3 = (ds.lat >= 15) & (ds.lat < 24) & (ds.lon > 260) & (ds.lon < 285)
      masks = [mask1, mask2, mask3]
      mastermask = mask1 | mask2 | mask3

      longr, latgr = np.meshgrid(ds.lon, ds.lat)

   print(ds)

   print(longr * ds)
   print(latgr)

   current += TSTEP
