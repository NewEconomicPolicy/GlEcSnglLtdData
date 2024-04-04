#-------------------------------------------------------------------------------
# Name:
# Purpose:     use multiprocessing to run Fortran Ecosse
# Author:      Mike Martin
# Created:     4 August 2017
# Description:  standard script derived from that written by Mark Richards
#-------------------------------------------------------------------------------
#
__author__ = 'soi698'
__prog__ = 'run_glec_sngl_ltd_data'
__version__ = '0.0'

import argparse
import json
import os
import tracemalloc
from os.path import abspath, expanduser, expandvars, normpath

from weather_datasets import record_weather_settings
from initialise_common_funcs import initiation, write_runsites_config_file
from glbl_ecsse_sngl_high_level_fns import generate_simulation_files

sleepTime = 5
PROGRAM_ID = 'glec_sngl'
BBOX_DEFAULT = [116.90045, 28.2294, 117.0, 29.0] # bounding box default - somewhere in SE Europe

def _read_config_file(form):
    """
    adapted from _read_config_file function in module initialise_sngl_funcs.py
    """
    func_name =  __prog__ +  ' _read_config_file'
    config_file = form.config_file
    try:
        with open(config_file, 'r') as fconfig:
            config = json.load(fconfig)
            print('Read config file ' + config_file)
    except (OSError, IOError) as err:
            print(err)
            return False

    mingui_list = ['weatherResource', 'aveWthrFlag', 'bbox', 'luPiJsonFname', 'hwsdCsvFname']
    grp = 'minGUI'
    for key in mingui_list:
        if key not in config[grp]:
            form.bbox = BBOX_DEFAULT
            form.csv_fname = ''
            print('{}\tError in group: {}'.format(func_name, grp))
            return False

    form.ave_weather_flag = config[grp]['aveWthrFlag']
    form.bbox = config[grp]['bbox']
    dum, dum, form.lon, form.lat = form.bbox

    form.weather_resource = config[grp]['weatherResource']
    form.wthr_coords_file = config[grp]['hwsdCsvFname']

    # land use and plant input
    # ========================
    lu_pi_json_fname = config[grp]['luPiJsonFname']
    form.lu_pi_json_fname = lu_pi_json_fname
    # print(check_lu_pi_json_fname(form))  # displays file info

    # common area
    # ===========
    grp = 'cmnGUI'
    try:
        form.study = config[grp]['study']
        hist_strt_year = config[grp]['histStrtYr']
        hist_end_year  = config[grp]['histEndYr']
        scenario       = config[grp]['climScnr']
        sim_strt_year  = config[grp]['futStrtYr']
        sim_end_year   = config[grp]['futEndYr']
        form.equimode = config[grp]['eqilMode']
    except KeyError:
        print('{0}\tError in group: {1}'.format(func_name,grp))
        return False

    # record weather settings
    # =======================
    form.wthr_settings_prev[form.weather_resource] = record_weather_settings(scenario, hist_strt_year, hist_end_year,
                                                                                        sim_strt_year, sim_end_year)
    form.hist_strt_year = int(hist_strt_year)
    form.hist_end_year = int(hist_end_year)
    form.scenario = scenario
    form.sim_strt_year = int(sim_strt_year)
    form.sim_end_year = int(sim_end_year)
    form.fstudy = ''

    form.depths = list([30, 100])  # soil depths - copied from common_componentsGUI.py

    # avoids errors when exiting
    # ==========================
    form.req_resol_deg = None
    form.req_resol_granul = None

    if form.python_exe is None or form.runsites_py is None or form.runsites_config_file is None:
        form.run_ecosse = False
    else:
        form.run_ecosse = True

    return True

class Form(object):
    '''
    Class to permit ECOSSE file generation in batch mode
    '''
    def __init__(self, config_file):
        '''

        '''
        self.version = 'HWSD_snglLtdData'
        self.study = 'Ajmer'
        initiation(self)
        _read_config_file(self)

        # TODO - lifted from common_sngl_cmpntsGUI.py
        # ===========================================
        self.lu_pi_content = {'YieldMap': '', 'LandusePI': {'0': ['Forestry', 9800.0], '50': ['Forestry', 0.0]}}
        luTypes = {};
        lu_type_abbrevs = {}
        for lu_type, abbrev, ilu in zip(
                ['Arable', 'Forestry', 'Miscanthus', 'Grassland', 'Semi-natural', 'SRC', 'Rapeseed', 'Sugar cane'],
                ['ara', 'for', 'mis', 'gra', 'nat', 'src', 'rps', 'sgc'],
                [1, 3, 5, 2, 4, 6, 7, 7]):
            luTypes[lu_type] = ilu
            lu_type_abbrevs[lu_type] = abbrev

        self.land_use_types = luTypes

    def generate_simulation(self):

        # tracemalloc.start()
        generate_simulation_files(self)

        # close various files
        if hasattr(self, 'fobjs'):
            for key in self.fobjs:
                self.fobjs[key].close()

        # close logging
        try:
            self.lgr.handlers[0].close()
        except AttributeError:
            pass

        # components of the command string have been checked at startup
        # =============================================================
        if write_runsites_config_file(self):
            # run the make simulations script
            # ===============================
            cmd_str = self.python_exe + ' ' + self.runsites_py + ' ' + self.runsites_config_file
            os.system(cmd_str)
        '''
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        print("[ Top 10 ]")
        for stat in top_stats[:10]:
            print(stat)
        '''
        return True

def main():
    '''
    Entry point
    '''
    argparser = argparse.ArgumentParser( prog = __prog__,
            description = 'Run ECOSSE for at one site in limited data mode.',
            usage = '{} configfile'.format(__prog__))

    argparser.add_argument('configfile', help = 'Full path of the config file.')
    argparser.add_argument('--version', action = 'version', version = '{} {}'.format(__prog__, __version__),
                                                                        help = 'Display the version number.')
    args = argparser.parse_args()

    args.config_file = abspath(normpath(expanduser(expandvars(args.configfile))))

    sim = Form(args.config_file)
    sim.generate_simulation()

if __name__ == '__main__':
    main()

