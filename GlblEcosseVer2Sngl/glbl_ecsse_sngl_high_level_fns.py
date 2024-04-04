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

__prog__ = 'glbl_ecsse_sngl_high_level_fns.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

import make_ltd_data_files
import getClimGenNC
import hwsd_bil
from prepare_ecosse_files import make_ecosse_file
from getClimGenFns import check_clim_nc_limits, associate_climate
# from runsites_high_level import run_ecosse_wrapper

def generate_simulation_files(form):
    '''
    called from GUI - generates ECOSSE simulation files for one site
    '''
    func_name =  __prog__ + ' generate_simulation_files'

    snglPntFlag = True

    if hasattr(form, 'w_study'):
        study = form.w_study.text()
        slon = form.w_ur_lon.text()
        weather_resource = form.combo10w.currentText()
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
    else:
        study = form.study
        lon_ur = form.lon
        lat_ur = form.lat
        weather_resource = form.weather_resource

    print('Gathering soil and climate data for study {}...\t\tin {}'.format(study,func_name))

    # extract required values from the HWSD database
    # ==============================================
    hwsd = hwsd_bil.HWSD_bil(form.lgr, form.hwsd_dir)
    nvals_read = hwsd.read_bbox_mu_globals([lon_ur, lat_ur], snglPntFlag)

    # retrieve dictionary mu_globals and number of occurrences
    # ========================================================
    mu_globals = hwsd.get_mu_globals_dict()
    if mu_globals is None:
        print('No soil records for this area\n')
        return

    # create and instantiate a new class NB this stanza enables single site
    # ==================================
    form.hwsd_mu_globals = type('test', (), {})()
    # form.hwsd_mu_globals.soil_recs = hwsd.get_soil_recs(sorted(mu_globals.keys()))
    form.hwsd_mu_globals.soil_recs = hwsd.get_soil_recs(mu_globals)
    if len(mu_globals) == 0:
        print('No soil data for this area\n')
        return

    mu_globals_props = {next(iter(mu_globals)): 1.0}

    mess = 'Retrieved {} values  of HWSD grid consisting of {} rows and {} columns: ' \
          '\n\tnumber of unique mu_globals: {}'.format(nvals_read, hwsd.nlats, hwsd.nlons, len(mu_globals))
    form.lgr.info(mess); print(mess)

    # check requested AOI coordinates against extent of the weather resource dataset
    # ==============================================================================
    bbox_aoi = list([lon_ur - 0.01, lat_ur - 0.01, lon_ur + 0.01, lat_ur + 0.01])
    if check_clim_nc_limits(form, weather_resource, bbox_aoi):
        print('Selected ' + weather_resource)
        historic_weather_flag = weather_resource
        future_climate_flag = weather_resource
    else:
        return

    form.historic_weather_flag = historic_weather_flag
    form.future_climate_flag = future_climate_flag
    climgen = getClimGenNC.ClimGenNC(form)

    # ==============================================================

    # generate weather dataset indices which enclose the AOI for this band
    num_band = 0
    aoi_indices_fut, aoi_indices_hist = climgen.genLocalGrid(bbox_aoi, hwsd, snglPntFlag, num_band)

    # historic weather and future climate
    # ===================================
    print('Getting future data for study {}'.format(study))
    wthr_rsrc = climgen.weather_resource
    if wthr_rsrc == 'NCAR_CCSM4':
        pettmp_fut = climgen.fetch_ncar_ccsm4_NC_data(aoi_indices_fut, num_band)

    elif wthr_rsrc == 'HARMONIE':
        pettmp_fut = climgen.fetch_harmonie_NC_data(aoi_indices_fut, num_band)

    elif wthr_rsrc == 'EObs':
        pettmp_fut = climgen.fetch_eobs_NC_data(aoi_indices_fut, num_band)

    elif wthr_rsrc in form.amma_2050_allowed_gcms:
        pettmp_fut = climgen.fetch_ewembi_NC_data(aoi_indices_fut, num_band)
    else:
        pettmp_fut = climgen.fetch_cru_future_NC_data(aoi_indices_fut, num_band)

    print('Getting historic data for study {}'.format(study))
    if wthr_rsrc == 'NCAR_CCSM4':
        pettmp_hist = climgen.fetch_ncar_ccsm4_NC_data(aoi_indices_hist, num_band, future_flag = False)

    elif wthr_rsrc == 'HARMONIE':
        pettmp_fut = climgen.fetch_harmonie_NC_data(aoi_indices_fut, num_band)

    elif wthr_rsrc == 'EObs':
        pettmp_hist = climgen.fetch_eobs_NC_data(aoi_indices_fut, num_band)

    elif wthr_rsrc in form.amma_2050_allowed_gcms:
        pettmp_hist = climgen.fetch_ewembi_NC_data(aoi_indices_hist, num_band, future_flag = False)
    else:
        pettmp_hist = climgen.fetch_cru_historic_NC_data(aoi_indices_hist, num_band)

    print('Creating simulation files for study {}...'.format(study))
    #      =========================================

    # Initialise the limited data object with general settings that do not change between simulations
    yrs_pi = None
    ltd_data = make_ltd_data_files.MakeLtdDataFiles(form, climgen, yrs_pi)  # create limited data object

    completed = 0
    skipped = 0

    # generate sets of Ecosse files for each site where each site has one or more soils
    # each soil can have one or more dominant soils
    # =======================================================================
    area = 1.0
    site_rec = list([hwsd.nrow1, hwsd.ncol1, lat_ur, lon_ur, area, mu_globals_props])

    # yield_set = associate_yield(form)
    pettmp_grid_cell = associate_climate(site_rec, climgen, pettmp_hist, pettmp_fut)
    if len(pettmp_grid_cell) == 0:
        skipped += 1
    else:
        make_ecosse_file(form, climgen, ltd_data, site_rec, study, pettmp_grid_cell)
        completed += 1

    print('Created {} simulation set in {}'.format(completed, form.sims_dir))

    # run further steps if requested
    # =============================
    # if form.w_auto_run_ec.isChecked():
    auto_run_flag = False
    if auto_run_flag:
        '''
        form.setup = {}
        form.setup['python_exe'] = 'E:\\Python38\\python.exe'
        form.setup['runsites_py'] = 'E:\\GlblEcosseVer2\\runsites.py'
        form.setup['runsites_config_file'] = 'F:\\GlobalEcosseOutputs\\config\\spatial_ecosse_config.txt'
        form.setup['sims_dir'] = form.sims_dir
        run_ecosse_wrapper(form)
        '''
        pass

    return

