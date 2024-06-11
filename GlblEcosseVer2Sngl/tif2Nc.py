"""
#-------------------------------------------------------------------------------
# Name:        glbl_ecsse_wthr_only_fns.py
# Purpose:     consist of high level functions invoked by main GUI
# Author:      Mike Martin
# Created:     05/02/2021
# Licence:     <your licence>
# Description:
#   generate weather from HWSD file
#-------------------------------------------------------------------------------
#
"""
__prog__ = 'tif2Nc.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

from os.path import join, isdir, isfile, split, splitext
from osgeo.gdal import Translate

def _cnvrt_tif_elev_nc():
    '''
    called from GUI
    requires gdal module:
        from osgeo import gdal
    '''
    base_dir = 'E:\\Faith_Sadiq\\elev_tif'
    out_dir = 'E:\\Faith_Sadiq\\elev_nc'

    tif_fn = join(base_dir, 'extract_dem' + '.tif')
    if isfile(tif_fn):
        nc_fn = join(out_dir, 'elev_high_def' + '.nc')
        if isfile(nc_fn):
            print(nc_fn + ' already exists')
        else:
            ds = Translate(nc_fn, tif_fn, format = 'NetCDF')
            print('Read {}\twrote {}'.format(tif_fn, nc_fn))

    return

def main():
    """
    Entry point
    """
    rc = _cnvrt_tif_elev_nc()

if __name__ == '__main__':
    main()