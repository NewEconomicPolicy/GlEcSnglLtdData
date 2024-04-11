"""
#-------------------------------------------------------------------------------
# Name:        hwsd_glblecsse_fns.py
# Purpose:     consist of high level functions invoked by main GUI
# Author:      Mike Martin
# Created:     11/12/2015
# Licence:     <your licence>
# Description:
#   comprises this function:
#       def generate_simulation_files(form)
#-------------------------------------------------------------------------------
#
"""
__prog__ = 'hwsd2_test.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

import hwsd_bil_v2

HWSD_DIR = 'E:\\HWSD_V2'

def test_hwsd2_db(form):
    """
    called from GUI - generates ECOSSE simulation files for one site
    """
    func_name =  __prog__ + ' generate_simulation_files'

    snglPntFlag = True

    slon = form.w_ur_lon.text()
    try:
        lon_ur = float(slon)
    except ValueError:
        print('Longitude must be a float')
        return

    slat = form.w_ur_lat.text()
    try:
        lat_ur = float(slat)
    except ValueError:
        print('Latitude must be a float')
        return

    # extract required values from the HWSD database
    # ==============================================
    hwsd = hwsd_bil_v2.HWSD_bil(form.lgr, HWSD_DIR)
    nvals_read = hwsd.read_bbox_mu_globals([lon_ur, lat_ur], snglPntFlag)

    # retrieve dictionary mu_globals and number of occurrences
    # ========================================================
    mu_globals = hwsd.get_mu_globals_dict()
    if mu_globals is None:
        print('No soil records for this area\n')
        return

    return

