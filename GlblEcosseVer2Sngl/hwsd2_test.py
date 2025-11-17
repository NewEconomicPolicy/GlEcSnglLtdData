"""
#-------------------------------------------------------------------------------
# Name:        hwsd2_test.py
# Purpose:     consist of high level functions invoked by main GUI
# Author:      Mike Martin
# Created:     11/11/2025
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

from pyodbc import connect, drivers
from os.path import join, isdir, isfile, split, splitext, exists, basename, splitdrive

from hwsd_bil_v2 import check_hwsd_integrity, HWSD_bil, fetch_accesss_cursor, get_soil_recs

HWSD_DIR = 'E:\\HWSD_V2'

ERROR_STR = '*** Error *** '

def test_hwsd2_db(form):
    """
    called from GUI - generates ECOSSE simulation files for one site
    """
    check_hwsd_integrity(HWSD_DIR)
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
    hwsd = HWSD_bil(form.lgr, HWSD_DIR)
    nvals_read = hwsd.read_bbox_mu_globals([lon_ur, lat_ur], snglPntFlag)

    # retrieve dictionary mu_globals and number of occurrences
    # ========================================================
    mu_globals = hwsd.get_mu_globals_dict()
    if mu_globals is None:
        print('No soil records for this area\n')
        return

    mu_globals = {3861: 1}

    # Accesss database
    # ================
    cursor = fetch_accesss_cursor(HWSD_DIR)
    if cursor is None:
        return

    # create and instantiate a new class NB this stanza enables single site
    # ==================================
    form.hwsd_mu_globals = type('test', (), {})()
    soil_recs = get_soil_recs(cursor, mu_globals)
    if len(soil_recs) == 0:
        print('No soil data for this area\n')
        return

    form.hwsd_mu_globals.soil_recs = soil_recs
    mu_globals_props = {next(iter(mu_globals)): 1.0}

    mess = 'Retrieved {} values  of HWSD grid consisting of {} rows and {} columns: ' \
           '\n\tnumber of unique mu_globals: {}'.format(nvals_read, hwsd.nlats, hwsd.nlons, len(mu_globals))
    form.lgr.info(mess);
    print(mess)

    return

