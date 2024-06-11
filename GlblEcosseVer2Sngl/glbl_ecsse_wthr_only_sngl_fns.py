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
__prog__ = 'glbl_ecsse_wthr_only_fns.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

from time import time
import csv
from os.path import join, isdir, isfile, split, splitext
from os import makedirs,walk
from glob import glob
from PyQt5.QtWidgets import QApplication

import getClimGenNC
import hwsd_bil
from prepare_ecosse_files import update_progress
from getClimGenFns import check_clim_nc_limits, associate_climate

try:
    from osgeo.gdal import Translate
    TRANS_FLAG = True
except ModuleNotFoundError as err:
    print(str(err))
    TRANS_FLAG = False

METRICS = list(['precipitation', 'temperature'])
WARNING_MESS = '*** Warning *** '

def _write_cnvrt_fert_organic_N_tiffs_to_nc(form):
    '''
    requires gdal module from osgeo
    '''
    base_dir = 'E:\\SuperG_MA\\staging_area_dsets\\fertiliser_manure\\N available from cattle goats and sheep'
    out_dir = 'E:\\SuperG_MA\\staging_area_dsets\\fertiliser_manure\\outputs_nc'

    base_dir = 'E:\\Mohamed\\datasets\\N_from_livestock'
    out_dir = 'E:\\Mohamed\\datasets\\N_from_livestock\\outputs_nc'

    for tif_fn in glob(base_dir + '\\*.tif'):
        root_name = splitext(split(tif_fn)[1])[0]
        nc_fn = join(out_dir, root_name + '.nc')
        if isfile(nc_fn):
            print(nc_fn + ' already exists')
        else:
            ds = Translate(nc_fn, tif_fn, format = 'NetCDF')
            print('Read {}\twrote {}'.format(tif_fn, nc_fn))

    return

def write_cnvrt_tiffs_to_nc_script(form):
    '''
    called from GUI
    '''
    if TRANS_FLAG:
        _write_cnvrt_fert_organic_N_tiffs_to_nc(form)
    else:
        mess = WARNING_MESS + 'this option requires the Translate function from the Geospatial Data'
        mess += '\n\t\t\tAbstraction Library (gdal) package from the OGGeo library'
        print(mess)

    return

def generate_weather_only(form):
    '''
    called from GUI
    '''
    study = form.w_study.text()
    wthr_rsrc = form.combo10w.currentText()

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

    # check requested AOI coordinates against extent of the weather resource dataset
    # ==============================================================================
    bbox_aoi = list([lon_ur - 0.01, lat_ur - 0.01, lon_ur + 0.01, lat_ur + 0.01])
    if check_clim_nc_limits(form, wthr_rsrc, bbox_aoi):
        print('\nGenerating weather for ' + study + ' from resource ' + wthr_rsrc)
        form.historic_weather_flag = wthr_rsrc
        form.future_climate_flag   = wthr_rsrc
    else:
        return

    # create climate object and generate weather dataset indices enclosing the AOI for the HWSD CSV dataset
    # ======================================================================================================
    climgen = getClimGenNC.ClimGenNC(form)
    sim_start_year = climgen.sim_start_year
    fut_start_year = form.weather_sets['EObs_Mnth']['year_start']
    mess = 'Simulation start year: {}\tfuture weather dataset start year: {}'.format(sim_start_year, fut_start_year)
    if fut_start_year > sim_start_year:
        print(mess + '\n\tsim start year must be same as or more recent than future dset start year')
        return
    print(mess)

    # Create and initialise CSV object
    # ================================
    wthr_csv = WthrCsvOutputs(form, climgen, study, lat_ur, lon_ur)
    wthr_csv.create_results_file()

    # extract required values from the HWSD database
    # ==============================================
    hwsd = hwsd_bil.HWSD_bil(form.lgr, form.hwsd_dir)
    gran_lat = int(round((90.0 - lat_ur) * hwsd.granularity))
    gran_lon = int(round((180.0 + lon_ur) * hwsd.granularity))
    aoi_indices_fut, aoi_indices_hist = climgen.genLocalGrid(bbox_aoi, hwsd, snglPntFlag = True)
    '''
    data in historic and future datasets is generally always present for any given grid cell, however, occasionally 
    data may be present in one but not the other 
    '''
    print('Getting future weather data')
    QApplication.processEvents()
    num_band = 0
    if wthr_rsrc == 'HARMONIE':
        pettmp_fut = climgen.fetch_harmonie_NC_data(aoi_indices_fut, num_band)
    elif wthr_rsrc == 'EObs':
        pettmp_fut = climgen.fetch_eobs_NC_data(aoi_indices_fut, num_band)
    else:
        pettmp_fut = climgen.fetch_cru_future_NC_data(aoi_indices_fut, num_band)

    print('Getting historic weather')
    QApplication.processEvents()
    if wthr_rsrc == 'HARMONIE':
        pettmp_fut = climgen.fetch_harmonie_NC_data(aoi_indices_fut, num_band)
    elif wthr_rsrc == 'EObs':
        pettmp_hist = climgen.fetch_eobs_NC_data(aoi_indices_fut, num_band)
    else:
        pettmp_hist = climgen.fetch_cru_historic_NC_data(aoi_indices_hist, num_band)

    # step through each cell
    # ======================
    skipped, completed, warning_count = 3*[0]
    last_time, start_time = 2*[time()]
    area = 1.0
    site_rec = list([gran_lat, gran_lon, lat_ur, lon_ur, area, None])

    pettmp_grid_cell = associate_climate(site_rec, climgen, pettmp_hist, pettmp_fut)
    if len(pettmp_grid_cell) == 0:
        print('*** Warning *** no weather data for site with lat: {}\tlon: {}'
              .format(round(site_rec[2], 3), round(site_rec[3], 3)))

    if len(pettmp_grid_cell['precipitation'][0]) == 0:
        mess = 'No historic weather data for lat/lon: {}/{}'.format(lat_ur, lon_ur)
        form.lgr.info(mess)
        skipped += 1

    wthr_csv.write_results(climgen, pettmp_grid_cell)

    completed += 1
    ncells = 1
    last_time = update_progress(last_time, start_time, completed, ncells, skipped, warning_count)

    # close CSV file
    # ==============
    wthr_csv.output_fhs.close()
    print('\nFinished processing')

    return

class WthrCsvOutputs(object):
    '''
    Class to write CSV results of a Spatial ECOSSE run
    '''
    def __init__(self, form, climgen, study, lat_ur, lon_ur):

        self.lgr = form.lgr
        self.varnames = list(['precip','tair'])
        self.sims_dir = form.sims_dir
        self.study = study
        self.header1 = ['Location: ' + study, 'Latitude: ' + str(lat_ur), 'Longitude: ' + str(lon_ur)]
        self.header2 = ['Date'] + METRICS

        self.sim_start_year = climgen.sim_start_year
        self.sim_end_year = climgen.sim_end_year

    def create_results_file(self):
        '''
        Create empty results files
        '''
        size_current = csv.field_size_limit(131072*4)

        # file creation
        # =============
        mess = 'Created '

        fname = self.study + '_weather.csv'
        try:
            self.output_fhs = open(join(self.sims_dir, fname), 'w', newline='')
            mess += fname + ' '
        except (OSError, IOError) as err:
            err_mess = 'Unable to open output file. {0}'.format(err)
            self.lgr.critical(err_mess)
            print(err_mess)


        self.writers = csv.writer(self.output_fhs, delimiter='\t')
        self.writers.writerow(self.header1)
        self.writers.writerow(self.header2)

        mess += 'in ' + self.sims_dir
        print(mess)

    def write_results(self, climgen, pettmp):
        '''
        Write data
        '''
        precip = pettmp[METRICS[0]][0]
        tair = pettmp[METRICS[1]][0]
        year = climgen.sim_start_year
        mnth = 1
        for precip, tair in zip(precip, tair):
            date_str = '{}-{:0>2}'.format(year, mnth)
            self.writers.writerow(list([date_str, round(precip, 2), round(tair, 2)]))
            mnth += 1
            if mnth > 12:
                mnth = 1
                year += 1