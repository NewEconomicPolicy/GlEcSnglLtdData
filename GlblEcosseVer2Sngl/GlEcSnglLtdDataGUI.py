# -------------------------------------------------------------------------------
# Name:
# Purpose:     Creates a GUI with five adminstrative levels plus country
# Author:      Mike Martin
# Created:     11/12/2015
# Licence:     <your licence>
# -------------------------------------------------------------------------------
# !/usr/bin/env python

__prog__ = 'GlEcSnglLtdDataGUI.py'
__version__ = '0.0.1'
__author__ = 's03mm5'

import sys
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QLabel, QWidget, QApplication, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit,
                                                                                QComboBox, QPushButton, QFileDialog)

from common_sngl_cmpntsGUI import (exitClicked, commonSection, changeConfigFile, studyTextChanged, saveClicked,
                                                                                                    granularToLatLons)
from glbl_ecsse_sngl_high_level_fns import generate_simulation_files
from initialise_sngl_funcs import read_config_file, check_lu_pi_json_fname, write_config_file
from initialise_common_funcs import initiation, write_runsites_config_file, build_and_display_studies
from weather_datasets import change_weather_resource
from glbl_ecsse_wthr_only_sngl_fns import generate_weather_only, write_cnvrt_tiffs_to_nc_script
from orator_wthr import generate_orator_wthr
from cvrtcoord import WGS84toOSGB36
from hwsd2_test import test_hwsd2_db

STD_FLD_SIZE_60 = 60
STD_FLD_SIZE_80 = 80
STD_FLD_SIZE_100 = 100
STD_FLD_SIZE_120 = 120
STD_FLD_SIZE_140 = 140
GRANULARITY = 120

class Form(QWidget):

    def __init__(self, parent=None):

        super(Form, self).__init__(parent)

        self.version = 'HWSD_snglLtdData'
        initiation(self)

        # define two vertical boxes, in LH vertical box put the painter and in RH put the grid
        # define horizon box to put LH and RH vertical boxes in
        hbox = QHBoxLayout()
        hbox.setSpacing(10)

        # left hand vertical box consists of png image
        # ============================================
        lh_vbox = QVBoxLayout()

        # LH vertical box contains image only
        lbl20 = QLabel()
        pixmap = QPixmap(self.fname_png)
        lbl20.setPixmap(pixmap)

        lh_vbox.addWidget(lbl20)

        # add LH vertical box to horizontal box
        hbox.addLayout(lh_vbox)

        # right hand box consists of combo boxes, labels and buttons
        # ==========================================================
        rh_vbox = QVBoxLayout()

        # The layout is done with the QGridLayout
        grid = QGridLayout()
        grid.setSpacing(10)  # set spacing between widgets

        # line 0
        # ======
        irow = 0
        lbl00 = QLabel('Study:')
        lbl00.setAlignment(Qt.AlignRight)
        grid.addWidget(lbl00, irow, 0)

        w_study = QLineEdit()
        w_study.setFixedWidth(STD_FLD_SIZE_120)
        grid.addWidget(w_study, irow, 1)
        self.w_study = w_study

        lbl00s = QLabel('studies:')
        lbl00s.setAlignment(Qt.AlignRight)
        helpText = 'list of studies'
        lbl00s.setToolTip(helpText)
        grid.addWidget(lbl00s, irow, 2)

        combo00s = QComboBox()
        for study in self.studies:
            combo00s.addItem(study)
        combo00s.setFixedWidth(STD_FLD_SIZE_120)
        grid.addWidget(combo00s, irow, 3)
        combo00s.currentIndexChanged[str].connect(self.changeConfigFile)
        self.combo00s = combo00s

        # line 2 - lon/lat
        # ================
        irow += 2
        lbl02a = QLabel('Longitude:')
        lbl02a.setAlignment(Qt.AlignRight)
        grid.addWidget(lbl02a, irow, 0)

        w_ur_lon = QLineEdit()
        w_ur_lon.setFixedWidth(STD_FLD_SIZE_60)
        grid.addWidget(w_ur_lon, irow, 1)
        self.w_ur_lon = w_ur_lon
        w_ur_lon.textChanged.connect(self.dsplyGranLatLon)

        lbl02b = QLabel('Latitude:')
        lbl02b.setAlignment(Qt.AlignRight)
        grid.addWidget(lbl02b, irow, 2)

        w_ur_lat = QLineEdit()
        w_ur_lat.setFixedWidth(STD_FLD_SIZE_60)
        grid.addWidget(w_ur_lat, irow, 3)
        self.w_ur_lat = w_ur_lat
        w_ur_lat.textChanged.connect(self.dsplyGranLatLon)

        # =======
        irow += 1
        lbl06a = QLabel('OSGB north/east:')
        lbl06a.setAlignment(Qt.AlignRight)
        grid.addWidget(lbl06a, irow, 0)

        lbl06 = QLabel()
        lbl06.setAlignment(Qt.AlignLeft)
        grid.addWidget(lbl06, irow, 1, 1, 2)
        self.lbl06 = lbl06

        # =======
        irow += 1
        lbl03a = QLabel('Granular long/lat:')
        lbl03a.setAlignment(Qt.AlignRight)
        grid.addWidget(lbl03a, irow, 0)

        lbl03 = QLabel()
        lbl03.setAlignment(Qt.AlignLeft)
        grid.addWidget(lbl03, irow, 1, 1, 2)
        self.lbl03 = lbl03

        # create lines to convert granular lat/lons to actual
        # ===================================================
        irow = granularToLatLons(self, grid, irow)
        irow += 1
        grid.addWidget(QLabel(''), irow, 1)     # spacer

        # ====================
        irow = commonSection(self, grid, irow)

        # row 16
        # ======
        irow += 1
        w_coords = QPushButton("Read coords file")
        helpText = 'Option to select an Excel file comprising coordinates for weather to be output'
        w_coords.setToolTip(helpText)
        w_coords.setFixedWidth(STD_FLD_SIZE_100)
        grid.addWidget(w_coords, irow, 0)
        w_coords.clicked.connect(self.fetchCoordsFile)

        w_lbl16 = QLabel('')
        grid.addWidget(w_lbl16, irow, 1, 1, 5)
        self.w_lbl16 = w_lbl16

        # action buttons
        # ==============
        irow += 2
        w_create_files = QPushButton("Create sim files")
        helpText = 'Generate ECOSSE simulation file sets corresponding to ordered HWSD global mapping unit set in CSV file'
        w_create_files.setToolTip(helpText)
        w_create_files.setEnabled(False)
        w_create_files.setFixedWidth(STD_FLD_SIZE_100)
        grid.addWidget(w_create_files, irow, 0)
        w_create_files.clicked.connect(self.createSimsClicked)
        self.w_create_files = w_create_files

        w_run_ecosse = QPushButton('Run Ecosse')
        helpText = 'Select this option to create a configuration file for the spec.py script and run it.\n' \
                   + 'The spec.py script runs the ECOSSE programme'
        w_run_ecosse.setFixedWidth(STD_FLD_SIZE_100)
        w_run_ecosse.setToolTip(helpText)
        w_run_ecosse.clicked.connect(self.runEcosseClicked)
        grid.addWidget(w_run_ecosse, irow, 1)
        self.w_run_ecosse = w_run_ecosse

        w_hwsd2 = QPushButton("Test HWSD2")
        helpText = 'Option to test HWSD2'
        w_hwsd2.setToolTip(helpText)
        w_hwsd2.setFixedWidth(STD_FLD_SIZE_100)
        grid.addWidget(w_hwsd2, irow, 2)
        w_hwsd2.clicked.connect(self.testHwsd2Clicked)

        w_save = QPushButton("Save")
        helpText = 'Save configuration and study definition files'
        w_save.setToolTip(helpText)
        grid.addWidget(w_save, irow, 3)
        w_save.clicked.connect(self.saveClicked)
        w_save.setFixedWidth(80)

        w_cancel = QPushButton("Cancel")
        helpText = 'Close GUI without saving configuration and study definition files'
        w_cancel.setToolTip(helpText)
        grid.addWidget(w_cancel, irow, 4)
        w_cancel.clicked.connect(self.cancelClicked)        

        w_exit = QPushButton("Exit", self)
        helpText = 'Close GUI - the configuration and study definition files will be saved'
        w_exit.setToolTip(helpText)
        grid.addWidget(w_exit, irow, 5)
        w_exit.clicked.connect(self.exitClicked)

        # line 20
        # =======
        irow += 1
        w_orator = QPushButton("Generate weather sheets")
        helpText = 'Generate weather sheets for ORATOR'
        w_orator.setToolTip(helpText)
        w_orator.setFixedWidth(STD_FLD_SIZE_140)
        grid.addWidget(w_orator, irow, 0)
        w_orator.clicked.connect(self.genWthrSheetsClicked)
        self.w_orator = w_orator
        w_orator.setEnabled(False)

        w_csv_wthr = QPushButton("CSV weather")
        helpText = 'Generate monthly and daily CSV weather'
        w_csv_wthr.setToolTip(helpText)
        w_csv_wthr.setFixedWidth(STD_FLD_SIZE_100)
        grid.addWidget(w_csv_wthr, irow, 1)
        w_csv_wthr.clicked.connect(self.genCsvWthrClicked)
        w_csv_wthr.setEnabled(False)
        self.w_csv_wthr = w_csv_wthr

        w_tif_to_nc  = QPushButton("GeoTiff to NC")
        helpText = 'Write script to convert GeoTiffs to NC files'
        w_tif_to_nc .setToolTip(helpText)
        grid.addWidget(w_tif_to_nc , irow, 2)
        w_tif_to_nc .clicked.connect(self.convertGeoTiffs)
        self.w_tif_to_nc  = w_tif_to_nc

        w_remove = QPushButton("Remove")
        helpText = 'Remove configuration file and all files associated with this project'
        w_remove.setToolTip(helpText)
        grid.addWidget(w_remove, irow, 4)
        w_remove.clicked.connect(self.removeProjectClicked)
        w_remove.setFixedWidth(80)
        w_remove.setEnabled(False)

        # add grid to RH vertical box
        rh_vbox.addLayout(grid)

        # vertical box goes into horizontal box
        hbox.addLayout(rh_vbox)

        # the horizontal box fits inside the window
        self.setLayout(hbox)

        # posx, posy, width, height
        self.setGeometry(300, 300, 690, 250)
        self.setWindowTitle('Global Ecosse - generate limited data mode ECOSSE input files for a single point')

        # reads and set values from last run
        # ==================================
        read_config_file(self)
        self.combo10w.currentIndexChanged[str].connect(self.weatherResourceChanged)

    def testHwsd2Clicked(self):
        """

        """
        study = self.w_study.text()
        if study == '':
            print('study cannot be blank')
            return

        self.study = study
        test_hwsd2_db(self)

    def convertGeoTiffs(self):
        """

        """
        write_cnvrt_tiffs_to_nc_script(self)

    def genCsvWthrClicked(self):
        """

        """
        generate_weather_only(self)

    def dsplyLatLon2Gran(self):
        """

        """
        lat, lon = 2*[-999]
        try:
            gran_lat = int(self.w_gran_lat.text())
            lat = round(90.0 - (gran_lat/GRANULARITY), 4)
        except ValueError:
            pass

        try:
            gran_lon = int(self.w_gran_lon.text())
            lon = round(gran_lon/GRANULARITY - 180.0, 4)
        except ValueError:
            pass

        mess = '{}\t{}'.format(lon, lat)
        self.lbl05.setText(mess)

    def dsplyGranLatLon(self):
        """
        returns a blank for latitude first time round
        """

        lat, lon, gran_lat, gran_lon = 4*[0]
        try:
            lat = float(self.w_ur_lat.text())
            gran_lat = int(round((90.0 - lat) * GRANULARITY))
        except ValueError:
            return

        try:
            lon = float(self.w_ur_lon.text())
            gran_lon = int(round((180.0 + lon) * GRANULARITY))
        except ValueError:
            pass

        mess = '{}\t{}'.format(gran_lon, gran_lat)
        self.lbl03.setText(mess)

        north, east = 2 * [-999]
        try:
            lat = float(self.w_ur_lat.text())
            north = int(round((90.0 - lat) * GRANULARITY))
        except ValueError:
            pass

        try:
            lon = float(self.w_ur_lon.text())
            east = int(round((180.0 + lon) * GRANULARITY))
        except ValueError:
            pass

        retcode = WGS84toOSGB36(lon, lat)
        east, north = retcode

        mess = '{}\t{}'.format(north, east)
        self.lbl06.setText(mess)

    def genWthrSheetsClicked(self):
        """

        """
        generate_orator_wthr(self)

    def weatherResourceChanged(self):
        """

        """
        change_weather_resource(self)

    def fetchLuPiJsonFile(self):
        """
        QFileDialog returns a tuple for Python 3.5, 3.6
        """
        fname = self.w_lbl13.text()
        fname, dummy = QFileDialog.getOpenFileName(self, 'Open file', fname, 'JSON files (*.json)')
        if fname != '':
            self.w_lbl13.setText(fname)
            self.w_lbl14.setText(check_lu_pi_json_fname(self))

    def fetchCoordsFile(self):
        """
        QFileDialog returns a tuple for Python 3.5, 3.6
        """
        fname = self.w_lbl16.text()
        fname, dummy = QFileDialog.getOpenFileName(self, 'Open file', fname, 'Excel files (*.xlsx)')
        if fname != '':
            self.w_lbl16.setText(fname)

    def studyTextChanged(self):
        """

        """
        studyTextChanged(self)

    def createSimsClicked(self):
        """

        """
        study = self.w_study.text()
        if study == '':
            print('study cannot be blank')
        else:
            self.study = study
            generate_simulation_files(self)

            #  save configuration settings
            # ===========================
            write_config_file(self, message_flag=False)

    def runEcosseClicked(self):
        """
        components of the command string have been checked at startup
        """
        if write_runsites_config_file(self):

            # run the make simulations script
            # ===============================
            cmd_str = self.python_exe + ' ' + self.runsites_py + ' ' + self.runsites_config_file
            os.system(cmd_str)

    def cancelClicked(self):
        """

        """
        exitClicked(self, write_config_flag=False)

    def exitClicked(self):
        """
        exit cleanly
        """
        exitClicked(self)

    def changeConfigFile(self):
        """
        permits change of configuration file
        """
        changeConfigFile(self)

    def removeProjectClicked(self):
        """

        """
        # remove_project(self)
        print('TODO: Not yet activated')

    def saveClicked(self):
        """
        check for spaces
        """
        study = self.w_study.text()
        if study == '':
            print('study cannot be blank')
        else:
            if study.find(' ') >= 0:
                print('*** study name must not have spaces ***')
            else:
                saveClicked(self)
                build_and_display_studies(self)

def main():
    """

    """
    app = QApplication(sys.argv)  # create QApplication object
    form = Form()  # instantiate form
    # display the GUI and start the event loop if we're not running batch mode
    form.show()  # paint form
    sys.exit(app.exec_())  # start event loop


if __name__ == '__main__':
    main()
