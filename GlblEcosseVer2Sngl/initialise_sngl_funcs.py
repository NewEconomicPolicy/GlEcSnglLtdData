"""
#-------------------------------------------------------------------------------
# Name:        initialise_sngl_funcs.py
# Purpose:     script to read read and write the setup and configuration files
# Author:      Mike Martin
# Created:     31/07/2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
"""

__prog__ = 'initialise_sngl_funcs.py'
__version__ = '0.0.0'

# Version history
# ---------------
# 
from os.path import join, isfile, exists
import json
from initialise_common_funcs import write_default_config_file, check_lu_pi_json_fname
from shape_funcs import calculate_area
from weather_datasets import change_weather_resource, record_weather_settings

BBOX_DEFAULT = [116.90045, 28.2294, 117.0, 29.0] # bounding box default - somewhere in SE Europe
sleepTime = 5

def read_config_file(form):
    """
    # read widget settings used in the previous programme session from the config file, if it exists,
    # or create config file using default settings if config file does not exist
    """
    func_name =  __prog__ +  ' read_config_file'
    config_file = form.config_file
    if exists(config_file):
        try:
            with open(config_file, 'r') as fconfig:
                config = json.load(fconfig)
                print('Read config file ' + config_file)
        except (OSError, IOError) as err:
                print(err)
                return False
    else:
        config = write_default_config_file(config_file)

    mingui_list = ['weatherResource', 'aveWthrFlag', 'bbox', 'luPiJsonFname', 'hwsdCsvFname']
    grp = 'minGUI'
    for key in mingui_list:
        if key not in config[grp]:
            form.bbox = BBOX_DEFAULT
            form.csv_fname = ''
            print('{}\tError in group: {}'.format(func_name, grp))
            return False

    # set check boxes
    # ===============
    ave_weather = config[grp]['aveWthrFlag']
    if ave_weather:
        form.w_ave_weather.setCheckState(2)
    else:
        form.w_ave_weather.setCheckState(0)

    form.bbox = config[grp]['bbox']

    weather_resource = config[grp]['weatherResource']
    form.combo10w.setCurrentText(weather_resource)
    change_weather_resource(form, weather_resource)

    wthr_coords_file = config[grp]['hwsdCsvFname']
    if isfile(wthr_coords_file):
        form.w_lbl16.setText(wthr_coords_file)
        form.w_orator.setEnabled(True)
    else:
        form.w_orator.setEnabled(False)

    # land use and plant input
    # ========================
    lu_pi_json_fname = config[grp]['luPiJsonFname']
    form.w_lbl13.setText(lu_pi_json_fname)
    form.w_lbl14.setText(check_lu_pi_json_fname(form))  # displays file info

    # common area
    # ===========
    grp = 'cmnGUI'
    try:
        form.w_study.setText(str(config[grp]['study']))
        hist_strt_year = config[grp]['histStrtYr']
        hist_end_year  = config[grp]['histEndYr']
        scenario       = config[grp]['climScnr']
        sim_strt_year  = config[grp]['futStrtYr']
        sim_end_year   = config[grp]['futEndYr']
        form.w_equimode.setText(str(config[grp]['eqilMode']))
    except KeyError:
        print('{0}\tError in group: {1}'.format(func_name,grp))
        return False

    # record weather settings
    # =======================
    form.wthr_settings_prev[weather_resource] = record_weather_settings(scenario, hist_strt_year, hist_end_year,
                                                                                        sim_strt_year, sim_end_year)
    form.combo09s.setCurrentText(hist_strt_year)
    form.combo09e.setCurrentText(hist_end_year)
    form.combo10.setCurrentText(scenario)
    form.combo11s.setCurrentText(sim_strt_year)
    form.combo11e.setCurrentText(sim_end_year)

    # ===================
    # bounding box set up
    # ===================
    area = calculate_area(form.bbox)
    ll_lon, ll_lat, ur_lon, ur_lat = form.bbox
    form.w_ur_lon.setText(str(ur_lon))
    form.w_ur_lat.setText(str(ur_lat))
    form.fstudy = ''

    # avoids errors when exiting
    # ==========================
    form.req_resol_deg = None
    form.req_resol_granul = None

    if form.python_exe is None or form.runsites_py is None or form.runsites_config_file is None:
        form.w_run_ecosse.setEnabled(False)

    return True

def write_config_file(form, message_flag = True):
    """
    # write current selections to config file
    """
    study = form.w_study.text()
    # facilitate multiple config file choices
    glbl_ecsse_str = form.glbl_ecsse_str
    config_file = join(form.config_dir, glbl_ecsse_str + study + '.txt')

    # prepare the bounding box
    # ========================
    ll_lon = 0.0; ll_lat = 0.0
    try:
        ur_lon = float(form.w_ur_lon.text())
        ur_lat = float(form.w_ur_lat.text())
    except ValueError as e:
        print('Problem writing bounding box to config file: ' + str(e))
        ur_lon = 0.0
        ur_lat = 0.0
    form.bbox =  list([ll_lon,ll_lat,ur_lon,ur_lat])

    # TODO: might want to consider where else in the work flow to save these settings
    weather_resource = form.combo10w.currentText()
    scenario         = form.combo10.currentText()
    hist_strt_year   = form.combo09s.currentText()
    hist_end_year    = form.combo09e.currentText()
    sim_strt_year    = form.combo11s.currentText()
    sim_end_year     = form.combo11e.currentText()
    form.wthr_settings_prev[weather_resource] = record_weather_settings(scenario, hist_strt_year, hist_end_year,
                                                                                        sim_strt_year, sim_end_year)
    sngl_point_flag = True
    hwsd_csv_fname  = ''
    grid_resol = ''

    config = {
        'minGUI': {
            'bbox'            : form.bbox,
            'snglPntFlag'     : sngl_point_flag,
            'weatherResource' : weather_resource,
            'aveWthrFlag'  : form.w_ave_weather.isChecked(),
            'hwsdCsvFname' : form.w_lbl16.text(),           # use obsolete config setting for coords file
            'luPiJsonFname': form.w_lbl13.text(),
            'usePolyFlag'  : False
        },
        'cmnGUI': {
            'study'     : form.w_study.text(),
            'histStrtYr': hist_strt_year,
            'histEndYr' : hist_end_year,
            'climScnr'  : scenario,
            'futStrtYr' : sim_strt_year,
            'futEndYr'  : sim_end_year,
            'eqilMode'  : form.w_equimode.text(),
            'gridResol' : grid_resol
            }
        }
    if isfile(config_file):
        descriptor = 'Overwrote existing'
    else:
        descriptor = 'Wrote new'
    if study != '':
        with open(config_file, 'w') as fconfig:
            json.dump(config, fconfig, indent=2, sort_keys=True)
            fconfig.close()
            if message_flag:
                print('\n' + descriptor + ' configuration file ' + config_file)
            else:
                print()

def write_study_definition_file(form):
    """
    # write study definition file
    """

    # do not write study def file
    # ===========================
    if 'LandusePI' not in form.lu_pi_content:
        return

    # prepare the bounding box
    # ========================
    ll_lon = 0.0; ll_lat = 0.0
    try:
        ur_lon = float(form.w_ur_lon.text())
        ur_lat = float(form.w_ur_lat.text())
    except ValueError:
        ur_lon = 0.0
        ur_lat = 0.0
    bbox =  list([ll_lon,ll_lat,ur_lon,ur_lat])
    study = form.w_study.text()

    weather_resource = form.combo10w.currentText()
    if weather_resource == 'CRU':
        fut_clim_scen = form.combo10.currentText()
    else:
        fut_clim_scen = weather_resource

    # construct land_use change - not elegant but adequate
    # =========================
    land_use = ''
    try:
        for indx in form.lu_pi_content['LandusePI']:
            lu, pi = form.lu_pi_content['LandusePI'][indx]
            land_use += form.lu_type_abbrevs[lu] + '2'
    except AttributeError as e:
        print(e)
        return

    land_use = land_use.rstrip('2')

    # ensure compatibility with spatial version
    # =========================================
    study_defn = {
        'studyDefn': {
            'bbox'     : bbox,
            "luPiJsonFname": form.w_lbl13.text(),
            'hwsdCsvFname' : '',
            'study'    : study,
            'land_use' : land_use,
            'histStrtYr': form.combo09s.currentText(),
            'histEndYr' : form.combo09e.currentText(),
            'climScnr' : fut_clim_scen,
            'futStrtYr': form.combo11s.currentText(),
            'futEndYr' : form.combo11e.currentText(),
            'province' : 'xxxx',
            'resolution': '',
            'shpe_file': 'xxxx',
            'version'  : form.version
            }
        }

    # copy to sims area
    # =================
    if study == '':
        print('*** Warning *** study not defined  - could not write study definition file')
    else:
        study_defn_file = join(form.sims_dir, study + '_study_definition.txt')
        with open(study_defn_file, 'w') as fstudy:
            json.dump(study_defn, fstudy, indent=2, sort_keys=True)
            print('\nWrote study definition file ' + study_defn_file)

    return
