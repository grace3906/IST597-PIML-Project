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
OUTPT = os.path.join(CMROOT, 'cmorph_vec_201801-201809.nc')

SLICE = slice(None, None, 2)

#apply masks piecewise and vectorize
#arrs: list of DataArrays to operate on
#masks: list of masks
def mask_vec(arrs, masks):
   toret = []
   #print(arrs)
   #print(masks)
   for ar in arrs:
       da_pieces = [ar.where(ms, drop=True) for ms in masks]
       #print([da.shape for da in da_pieces])
       vecs = [da.values.ravel() for da in da_pieces]
       toret.append(np.concatenate(vecs))

   return toret

current = start
masks, mastermask = None, None
longr, latgr = None, None
outds = None
while current <= end:
   folder = os.path.join(CMROOT, str(current.year), current.strftime('%m'), current.strftime('%d'))
   filefill = current.strftime('%Y%m%d%H')
   #print(FILSTR % filefill)

   ds = xr.open_dataset(os.path.join(folder, FILSTR % filefill))
   ds = ds.sel(lon=ds.lon[SLICE], lat=ds.lat[SLICE], time=current)
   #print(ds)

   if current == start:
      mask1 = (ds.lat >= 42) & (ds.lat < 52) & (ds.lon > 230) & (ds.lon < 265)
      mask2 = (ds.lat >= 24) & (ds.lat < 42) & (ds.lon > 230) & (ds.lon < 285)
      mask3 = (ds.lat >= 15) & (ds.lat < 24) & (ds.lon > 260) & (ds.lon < 285)
      masks = [mask1, mask2, mask3]
      mastermask = mask1 | mask2 | mask3

      longr, latgr = np.meshgrid(ds.lon, ds.lat)
      longr = xr.DataArray(longr, dims=['lat', 'lon'], coords=[ds.lat, ds.lon])
      latgr = xr.DataArray(latgr, dims=['lat', 'lon'], coords=[ds.lat, ds.lon])

   #print(((longr * ds.cmorph) == (ds.lon * ds.cmorph)).all())
   #print(((longr * ds.cmorph) - (ds.lon * ds.cmorph)).max())
   #print(((latgr * ds.cmorph) - (ds.lat * ds.cmorph)).max())
   #print(latgr.sel(lat=59, method='nearest').values)
   #print(latgr.where(masks[0], drop=True))

   vecs = mask_vec([ds.cmorph, latgr, longr], masks)
   vecdas = [xr.DataArray(vv[None, :], dims=['time', 'idx'], coords=[[current], np.arange(vv.shape[0])]) for vv in vecs]
   #print([vv.shape for vv in vecs])

   vecds = xr.Dataset(data_vars=dict(pmmhr=vecdas[0], lat=vecdas[1], lon=vecdas[2]))
   #print(vecds)
   if current == start:
      outds = vecds
   else:
      outds = xr.concat((outds, vecds), dim='time')

   if current.hour == 0 and current.minute == 0:
      print(current)
      outds.to_netcdf(OUTPT)

   current += TSTEP
