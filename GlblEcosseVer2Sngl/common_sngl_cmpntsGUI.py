"""
#-------------------------------------------------------------------------------
# Name:
# Purpose:     consist of high level functions invoked by main GUI
# Author:      Mike Martin
# Created:     11/12/2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#
"""

__prog__ = 'common_sngl_cmpntsGUI.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

from os.path import normpath, isfile

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox

from initialise_sngl_funcs import write_study_definition_file, read_config_file, write_config_file
STD_FLD_SIZE_60 = 60
STD_FLD_SIZE_80 = 80
STD_FLD_SIZE_100 = 100
STD_BTN_SIZE = 100

def granularToLatLons(form, grid, irow):
    """

    """
    irow += 1
    lbl04a = QLabel('Granular long:')
    lbl04a.setAlignment(Qt.AlignRight)
    grid.addWidget(lbl04a, irow, 0)

    w_gran_lon = QLineEdit()
    w_gran_lon.setFixedWidth(STD_FLD_SIZE_60)
    grid.addWidget(w_gran_lon, irow, 1)
    form.w_gran_lon = w_gran_lon
    w_gran_lon.textChanged.connect(form.dsplyLatLon2Gran)

    lbl04b = QLabel('Granular lat:')
    lbl04b.setAlignment(Qt.AlignRight)
    grid.addWidget(lbl04b, irow, 2)

    w_gran_lat = QLineEdit()
    w_gran_lat.setFixedWidth(STD_FLD_SIZE_60)
    grid.addWidget(w_gran_lat, irow, 3)
    form.w_gran_lat = w_gran_lat
    w_gran_lat.textChanged.connect(form.dsplyLatLon2Gran)

    # line 3
    # =======
    lbl05a = QLabel('Long/lat:')
    lbl05a.setAlignment(Qt.AlignRight)
    grid.addWidget(lbl05a, irow, 4)

    lbl05 = QLabel()
    lbl05.setAlignment(Qt.AlignLeft)
    grid.addWidget(lbl05, irow, 5, 1, 2)
    form.lbl05 = lbl05

    return irow

def commonSection(form, grid, irow):
    """

    """
    # hist_syears, hist_eyears, fut_syears, fut_eyears, scenarios = get_weather_parms(form, 'CRU')
    equimodeDflt = '9.5'
    form.depths = list([30,100]) # soil depths

    luTypes = {}; lu_type_abbrevs = {}
    for lu_type, abbrev, ilu in zip(
                    ['Arable','Forestry','Miscanthus','Grassland','Semi-natural', 'SRC', 'Rapeseed', 'Sugar cane'],
                    ['ara',   'for',      'mis',      'gra',      'nat',          'src', 'rps',      'sgc'],
                    [1,        3,          5,          2,          4,              6,     7,          7]):
        luTypes[lu_type] = ilu
        lu_type_abbrevs[lu_type] = abbrev

    form.land_use_types = luTypes
    form.lu_type_abbrevs = lu_type_abbrevs

    # resources
    # =========
    irow += 1
    lbl10w = QLabel('Weather resource')
    lbl10w.setAlignment(Qt.AlignRight)
    helpText = 'permissable weather dataset resources include CRU, Euro-CORDEX - see: http://www.euro-cordex.net, MERA and EObs'
    lbl10w.setToolTip(helpText)
    grid.addWidget(lbl10w, irow, 0)

    combo10w = QComboBox()
    combo10w.setFixedWidth(STD_FLD_SIZE_100)
    for weather_resource in form.weather_resources_generic:
        combo10w.addItem(weather_resource)
    form.combo10w = combo10w
    grid.addWidget(combo10w, irow, 1)

    # scenarios
    # =========
    lbl10 = QLabel('Climate Scenario')
    lbl10.setAlignment(Qt.AlignRight)
    helpText = 'Ecosse requires future average monthly precipitation and temperature derived from climate models.\n' \
        + 'The data used here is ClimGen v1.02 created on 16.10.08 developed by the Climatic Research Unit\n' \
        + ' and the Tyndall Centre. See: http://www.cru.uea.ac.uk/~timo/climgen/'

    lbl10.setToolTip(helpText)
    grid.addWidget(lbl10, irow, 2)

    # use filler scenarios, start and years - these are populated when the configuration file is read
    # ===============================================================================================
    combo10 = QComboBox()
    combo10.setFixedWidth(STD_FLD_SIZE_80)
    form.combo10 = combo10
    grid.addWidget(combo10, irow, 3)

    # =======
    irow += 1
    lbl09s = QLabel('Historic start year')
    lbl09s.setAlignment(Qt.AlignRight)
    helpText = 'Ecosse requires long term average monthly precipitation and temperature\n' \
            + 'which is derived from datasets managed by Climatic Research Unit (CRU).\n' \
            + ' See: http://www.cru.uea.ac.uk/about-cru'
    lbl09s.setToolTip(helpText)
    grid.addWidget(lbl09s, irow, 0)

    combo09s = QComboBox()
    combo09s.setFixedWidth(STD_FLD_SIZE_60)
    grid.addWidget(combo09s, irow, 1)
    form.combo09s = combo09s

    lbl09e = QLabel('End year')
    lbl09e.setAlignment(Qt.AlignRight)
    grid.addWidget(lbl09e, irow, 2)

    combo09e = QComboBox()
    combo09e.setFixedWidth(STD_FLD_SIZE_60)
    grid.addWidget(combo09e, irow, 3)
    form.combo09e = combo09e

    # years into future
    # =================
    irow += 1
    lbl11s = QLabel('Simulation start year')
    helpText = 'Simulation start and end years determine the number of growing seasons to simulate\n' \
                                            + 'CRU and CORDEX resources run to 2100 whereas EObs resource runs to 2017'
    lbl11s.setToolTip(helpText)
    lbl11s.setAlignment(Qt.AlignRight)
    grid.addWidget(lbl11s, irow, 0)

    combo11s = QComboBox()
    combo11s.setFixedWidth(STD_FLD_SIZE_60)
    grid.addWidget(combo11s, irow, 1)
    form.combo11s = combo11s

    lbl11e = QLabel('End year')
    lbl11e.setAlignment(Qt.AlignRight)
    grid.addWidget(lbl11e, irow, 2)

    combo11e = QComboBox()
    combo11e.setFixedWidth(STD_FLD_SIZE_60)
    grid.addWidget(combo11e, irow, 3)
    form.combo11e = combo11e
    
    w_ave_weather = QCheckBox('Use average weather')
    helpText = 'Select this option to use average weather, from the CRU year range, for\n' \
               ' the climate file for each of the simulation years'
    w_ave_weather.setToolTip(helpText)
    grid.addWidget(w_ave_weather, irow, 4, 1, 2)
    form.w_ave_weather = w_ave_weather

    # equilibrium mode
    # ================
    irow += 1
    lbl12 = QLabel('Equilibrium mode')
    lbl12.setAlignment(Qt.AlignRight)
    helpText = 'mode of equilibrium run, generally OK with 9.5'
    lbl12.setToolTip(helpText)
    grid.addWidget(lbl12, irow, 0)

    w_equimode = QLineEdit()
    w_equimode.setText(equimodeDflt)
    w_equimode.setFixedWidth(STD_FLD_SIZE_60)
    form.w_equimode = w_equimode
    grid.addWidget(w_equimode, irow, 1)

    # row 13
    # ======
    irow += 1
    w_lu_pi_file = QPushButton("Landuse PI file")
    w_lu_pi_file.setFixedWidth(STD_FLD_SIZE_100)
    helpText = 'Option to select a JSON file comprising year index, landuse and plant input (tonnes per hectare)'
    w_lu_pi_file.setToolTip(helpText)
    grid.addWidget(w_lu_pi_file, irow, 0, alignment=Qt.AlignRight)
    w_lu_pi_file.clicked.connect(form.fetchLuPiJsonFile)

    w_lbl13 = QLabel('')
    grid.addWidget(w_lbl13, irow, 1, 1, 5)
    form.w_lbl13 = w_lbl13

    # for message from check_lu_pi_json_fname
    # =======================================
    irow += 1
    w_lbl14 = QLabel('')
    grid.addWidget(w_lbl14, irow, 1, 1, 5)
    form.w_lbl14 = w_lbl14

    return irow

def saveClicked(form):
    """
    write last GUI selections
    """
    write_config_file(form)
    write_study_definition_file(form)
    return

def exitClicked(form, write_config_flag = True):
    """
    write last GUI selections
    """
    if write_config_flag:
        write_config_file(form)
        write_study_definition_file(form)

    # close various files
    # ===================
    if hasattr(form, 'fobjs'):
        for key in form.fobjs:
            form.fobjs[key].close()

    # close logging
    # =============
    try:
        form.lgr.handlers[0].close()
    except AttributeError:
        pass

    form.close()
    return

def changeConfigFile(form):
    """
    identify and read the new configuration file
    """
    new_study = form.combo00s.currentText()
    new_config = 'global_ecosse_config_sngl_' + new_study
    config_file = normpath(form.config_dir + '/' + new_config + '.txt')

    if isfile(config_file):
        form.config_file = config_file
        read_config_file(form)
        form.study = new_study
        form.w_study.setText(new_study)
    else:
        print('Could not locate ' + config_file)

    return

def studyTextChanged(form):
    """
    replace spaces with underscores and rebuild study list
    """

    study = form.w_study.text()
    form.w_study.setText(study.replace(' ','_'))

    return