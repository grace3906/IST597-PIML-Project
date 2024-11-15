import os
import glob
import numpy as np
import xarray as xr
from datetime import datetime, timedelta
import cftime

# Start and end dates
start = cftime.DatetimeJulian(2018, 9, 1, 0, 0)
end = cftime.DatetimeJulian(2018, 9, 30, 23, 30)
TSTEP = timedelta(minutes=30)

IMROOT = '/glade/work/jpan/IMERG/gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGHH.07/'
FILSTR = '3B-HHR.MS.MRG.3IMERG.%s-S%s-E*.V07B.HDF5'
h5grp = '/Grid'
pvar = 'precipitation'
OUTPT = os.path.join(IMROOT, 'IMERG_vec_201809.nc')

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
   folder = os.path.join(IMROOT, str(current.year), "{:03d}".format(current.timetuple().tm_yday))
   filldate = current.strftime('%Y%m%d')
   filltime = current.strftime('%H%M%S')
   #print(FILSTR % filefill)
   fullpath = glob.glob(os.path.join(folder, FILSTR % (filldate, filltime)))[0]

   ds = xr.open_dataset(fullpath, group=h5grp, engine='h5netcdf')
   #print(ds.time)
   ds = ds.sel(lon=ds.lon[SLICE], lat=ds.lat[SLICE], time=current)
   ds.coords['lon'] = (ds.coords['lon'] + 180) % 360
   #print(ds.precipitation.attrs)

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

   #print(masks[0].sum())
   vecs = mask_vec([ds[pvar], latgr, longr], masks)
   if np.isnan(vecs[0]).sum():
      print('NaNs found %s' % str(current))
   if (vecs[0] == -9999.9).sum():
      print('-9999.9 found %s' % str(current))
   vecdas = [xr.DataArray(vv[None, :], dims=['time', 'idx'], coords=[[current], np.arange(vv.shape[0])]) for vv in vecs]
   #vecdas = [xr.DataArray(vecs[0][None, :], dims=['time', 'idx'], coords=[[current], np.arange(vecs[0].shape[0])])]
   #[vecdas.append(xr.DataArray(vv, dims=['idx'], coords=[np.arange(vv.shape[0])])) for vv in vecs[1:]]
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
