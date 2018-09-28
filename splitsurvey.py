# -*- coding: utf-8 -*-
"""
Created on Mon Sep 04 12:21:43 2017

Interactive application to allow splitting of SEG-Y data by location.

@author: kb
"""

import sys
import pickle
from PyQt5 import QtGui, QtCore, QtWidgets
from obspy.core import read
from obspy import Stream
from pyproj import Proj
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from utils import *

class Window(QtWidgets.QMainWindow): 
    def __init__(self, parent = None):
        super(Window, self).__init__(parent)
        #super().__init__()
        
        self.setWindowIcon(QtGui.QIcon('png/icon.png'))
        self.setWindowTitle('SplitSURVEY')
        
        # figure
        self.figure = Figure()
        self.figure.set_facecolor('None')

        # canvas for figure
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        
        # custom navigation toolbar class to include a settings option
        self.toolbar = CustomToolbar(self.canvas, self)

        # button connected to `plot` method
        self.button_plot = QtWidgets.QPushButton('Plot')
        self.button_plot.clicked.connect(self.plotSURVEY)
        self.button_plot.setMaximumWidth(100)
        
        self.button_split = QtWidgets.QPushButton('Split Survey')
        self.button_split.clicked.connect(self.splitSURVEY)
        self.button_split.setMaximumWidth(100)
        
        self.button_previous = QtWidgets.QPushButton('<')
        self.button_previous.setMaximumWidth(100)
        self.button_previous.clicked.connect(self.previous_func)
        self.button_previous.setToolTip('N')
        self.button_next = QtWidgets.QPushButton('>')
        self.button_next.setMaximumWidth(100)
        self.button_next.clicked.connect(self.next_func)
        self.button_next.setToolTip('M')
        self.button_add_split = QtWidgets.QPushButton('Add Split')
        self.button_add_split.setMaximumWidth(100)
        self.button_add_split.clicked.connect(self.split_func)
        self.button_add_split.setToolTip('Z')
        self.button_clear_split = QtWidgets.QPushButton('Clear Splits')
        self.button_clear_split.setMaximumWidth(100)
        self.button_clear_split.clicked.connect(self.clear_split_func)
        self.button_clear_split.setToolTip('C')
        self.button_delete_last_split = QtWidgets.QPushButton('Undo Split')
        self.button_delete_last_split.setToolTip('X')
        self.button_delete_last_split.setMaximumWidth(100)
        self.button_delete_last_split.clicked.connect(self.delete_last_split)
        
        #picker mode
        self.picker_mode = QtWidgets.QComboBox(self)
        self.picker_mode.addItem("Split")
        self.picker_mode.addItem("Extract")
        self.picker_mode.setMaximumWidth(100)
        self.picker_mode_label = QtWidgets.QLabel('Picker Mode: ')
        
        #Splits I/O
        self.button_output_splits = QtWidgets.QPushButton('Export Split File')
        self.button_output_splits.setMaximumWidth(100)
        self.button_output_splits.clicked.connect(self.output_split_list_menu)
        self.button_import_splits = QtWidgets.QPushButton('Import Split File')
        self.button_import_splits.setMaximumWidth(100)
        self.button_import_splits.clicked.connect(self.import_split_log)
        
        self.button_export_survey = QtWidgets.QPushButton('Export Survey')
        self.button_export_survey.setMaximumWidth(100)
        self.button_export_survey.clicked.connect(self.export_survey)
        
        self.button_import_survey = QtWidgets.QPushButton('Import Survey')
        self.button_import_survey.setMaximumWidth(100)
        self.button_import_survey.clicked.connect(self.import_survey)
        # File Browser
        self.browse = QtWidgets.QPushButton('Browse')
        self.browse.clicked.connect(self.get_survey_folder_name)
        self.browse.setMaximumWidth(100)
        
        self.output_button = QtWidgets.QPushButton('Output Folder')
        self.output_button.clicked.connect(self.get_foldername)
        self.output_button.setMaximumWidth(100)
        
        #path variables for I/O
        self.foldername = None
        self.fname = None
        self.prefix_box = QtWidgets.QLineEdit(self)
        self.cruise_id_label = QtWidgets.QLabel('Cruise ID')
        #File name as self.lbl
        self.lbl = QtWidgets.QLabel('No input file selected')
        self.lbl2 = QtWidgets.QLabel('No output folder selected')
        self.statuslbl = QtWidgets.QLabel('Ready!')
        self.statuslbl.setIndent(5)
        
        #progress bar to monitor split and plot
        self.progress = QtWidgets.QProgressBar(self)
        self.completed = 0
        
        #spacers
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        # set the layout where:
        # numbers are   (y coordinate from top left,
        #                   x coordinate from left,
        #                   ?,
        #                   how many grid cells the item spans)
        layout = QtWidgets.QGridLayout()
        layout.addWidget(self.toolbar,0,0,1,10)
        layout.addWidget(self.canvas,1,0,1,10)
        
        layout.addWidget(self.browse,2,0,1,1)
        layout.addWidget(self.lbl,2,1,1,7)
        layout.addWidget(self.picker_mode_label,2,8,1,1)
        layout.addWidget(self.picker_mode,2,9,1,1)
        
        layout.addWidget(self.output_button,3,0,1,1)
        layout.addWidget(self.lbl2,3,1,1,7)
        layout.addWidget(self.button_export_survey,3,8,1,1)
        layout.addWidget(self.button_import_survey,3,9,1,1)
        
        layout.addWidget(self.cruise_id_label,4,0,1,1)
        layout.addWidget(self.prefix_box,4,1,1,9)
        
        layout.addWidget(self.button_plot,5,0,1,1)
        layout.addWidget(self.button_previous,5,1,1,1)
        layout.addWidget(self.button_next,5,2,1,1)
        layout.addWidget(self.button_add_split,5,3,1,1)
        layout.addWidget(self.button_delete_last_split,5,4,1,1)
        layout.addWidget(self.button_clear_split,5,5,1,1)
        layout.addWidget(self.button_split,5,6,1,1)
        layout.addWidget(self.button_output_splits,5,7,1,1)
        layout.addWidget(self.button_import_splits,5,8,1,1)
        layout.addItem(spacerItem1,5,9,1,1)
        
        layout.addWidget(self.statuslbl,6,0,3,10)
        layout.addWidget(self.progress,7,0,1,10)
        
        self.setCentralWidget(QtWidgets.QWidget(self))
        self.centralWidget().setLayout(layout)
        #self.setLayout(layout)
        self.initiate_variables()
    def initiate_variables(self):
        self.split = []
        self.split_x = []
        self.split_y = []
        self.lastind = 0
        
        self.traceno = []; self.starttime = []; self.lon = []; self.lat = []; self.xs = []; self.ys = []; self.endtime = []; self.cumulative_trace_number = []
        # create an axis
        self.ax = self.figure.add_subplot(111)
        
        
        #label axes
        self.ax.set_xlabel('Easting (m)')
        self.ax.set_ylabel('Northing (m)')
        self.ax.grid(b=True, color='black', linestyle='--', linewidth=0.5, alpha=0.5)
        
        self.figure.tight_layout()
        
        self.text = self.ax.text(0.05, 0.95, 'Trace: none',
                            transform=self.ax.transAxes, va='top')
        self.selected, = self.ax.plot(self.xs, self.ys, 'x', ms=12, alpha=0.4,
                                 color='black', visible=False)
        self.split_points, = self.ax.plot(self.split_x, self.split_y, 'o', ms=12, alpha=0.4,
                                 color='red', visible=False)
        
    def onpress(self, event):
        """
        Iterate through traces with m and n keys
        """
        if self.lastind is None:
            return
        if event.key not in ('n', 'm'):
            return
        if event.key == 'm':
            inc = 1
        else:
            inc = -1

        self.lastind += inc
        self.lastind = np.clip(self.lastind, 0, len(self.ys) - 1)
        self.update()
    def split_func(self):
        """
        Function called when a split is added
        """
        self.split.append(self.lastind)
        self.split_x.append(self.xs[self.lastind])
        self.split_y.append(self.ys[self.lastind])
        self.update()
    def clear_split_func(self):
        """
        Clears the list of splits, so you can start over.
        """
        self.split = []
        self.split_x = []
        self.split_y = []
        self.update()
    def delete_last_split(self):
        """
        Undo function to remove the last split added
        """
        self.split = self.split[:-1]
        self.split_x = self.split_x[:-1]
        self.split_y = self.split_y[:-1]
        self.update()
    def previous_func(self):
        """
        Moves selection back one trace
        """
        self.lastind += -1
        self.lastind = np.clip(self.lastind, 0, len(self.ys) - 1)
        self.update()
    def next_func(self):
        """
        Moves selection forward one trace
        """
        self.lastind += 1
        self.lastind = np.clip(self.lastind, 0, len(self.ys) - 1)
        self.update()
    def export_survey(self): 
        """
        Function to save the navigation from the lines to a external file so it can be recalled later
        """
        path, junk = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
        survey_dict = {"traceno": self.traceno,"xs": self.xs, "ys": self.ys, "lat":self.lat,"lon":self.lon,"starttime":self.starttime,
                    "endtime":self.endtime, "segy_list":self.segy_list, "file_dictionary":self.file_dictionary,"cumulative_trace_number":self.cumulative_trace_number}
        with open(path, 'wb') as f:
            pickle.dump(survey_dict, f)
    def import_survey(self):
        """
        Function to import a previously saved navigation/survey file
        """
        temp_fname,junk = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file')
        with open(temp_fname, 'rb') as f:
            survey_dict = pickle.load(f)
        self.traceno = survey_dict["traceno"]
        self.xs = survey_dict["xs"]
        self.ys = survey_dict["ys"]
        self.lon = survey_dict["lon"]
        self.lat = survey_dict["lat"]
        self.starttime = survey_dict["starttime"]
        self.endtime = survey_dict["endtime"]
        self.segy_list = survey_dict["segy_list"]
        self.file_dictionary = survey_dict["file_dictionary"]
        self.cumulative_trace_number = survey_dict["cumulative_trace_number"]
        
        #plot
        self.ax.set_aspect('equal', 'datalim')
        
        #plot nav
        self.line, = self.ax.plot(self.xs, self.ys, '-', picker=5)
        
        self.update_progress(75)
        
        #connect matplotlib events
        self.canvas.mpl_connect('pick_event', self.onpick)
        self.canvas.mpl_connect('key_press_event', self.onpress)
        self.canvas.mpl_connect('key_press_event', self.splitkeys)
        self.canvas.draw()
        
        self.update_progress(100)
        self.statuslbl.setText('Ready!')
        
        self.update()
    def init_navlog(self,path):
        """
        Initiates a log file that is written to whenever a trace with missing navigation is found
        """
        f = open(path,'w')
        f.write('splitSURVEY Navigation Log'
                +'\nError,Filename,Trace,Starttime')
        f.close()
    def enter_navlog(self, path, string):
        """
        Enters text into the navigation log
        """
        with open(path, 'a') as f:
            f.write('\n'+ string)
    def init_logfile(self,path):
        """
        Initiates a log file that records an index of the output segy files. Called when 'Split Survey' is pressed.
        """
        f = open(path,'w')
        f.write('\t'+'SOL'+'\t'+'EOL'+'\t'+'Number of output files')
        f.close()
    def enter_line_in_logfile(self,path,linenumber,chunk):
        """
        Enters a line in the line log file documenting the start and end time of the exported lines
        """
        SOL = self.starttime[chunk[0]].datetime.strftime('%j %H:%M:%S')
        EOL = self.endtime[chunk[-1]].datetime.strftime('%j %H:%M:%S')
        if (chunk[-1]-chunk[0])>26000:
            number_of_files = 1 + (chunk[-1]-chunk[0])//26000
        else:
            number_of_files = 1
        with open(path, 'a') as f:
            f.write('\n'+ 'Line ' + str(linenumber+1) + '\t' + SOL + '\t' + EOL + '\t' + str(number_of_files))
    def output_split_list(self,path,list_of_splits,split_x,split_y):
        """
        Outputs a saved version of the splits so they can be recalled later
        """
        split_dict = {"split": self.split,"split_x": self.split_x, "split_y": self.split_y}
        with open(path, 'wb') as f:
            pickle.dump(split_dict, f)
    def output_split_list_menu(self):
        """
        Wrapped for output_split_list. Called when 'Export Splits' is pressed.
        """
        name, junk = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
        self.output_split_list(name, self.split, self.split_x, self.split_y)
    def import_split_log(self):
        """
        Allows importing a previously saved splits file
        """
        temp_fname,junk = QtWidgets.QFileDialog.getOpenFileName(self, 'Select file')
        with open(temp_fname, 'rb') as f:
            split_dict = pickle.load(f)
        self.split = split_dict["split"]
        self.split_x = split_dict["split_x"]
        self.split_y = split_dict["split_y"]
        self.update()
    def splitkeys(self,event):
        """
        Choose traces to split the line, z key to split, x key to clear, c to undo last split.
        """
        if event.key not in ('z','x','c'):
            return
        #add to list of split points by pressing z
        if event.key == 'z':
            self.split_func()
        #clear split points by pressing c
        if event.key == 'c':
            self.clear_split_func()
        #undo last split by pressing x
        if event.key == 'x':
            self.delete_last_split()
    def onpick(self, event):
        """
        Function called when you select from the navigation.
        
        TODO: add different functionality for different modes (e.g. Extract) - not implemented yet
        """
        if str(self.picker_mode.currentText()) == "Split":
            if event.artist != self.line:
                return True
            
            N = len(event.ind)
            if not N:
                return True
            
            # the click locations
            x = event.mouseevent.xdata
            y = event.mouseevent.ydata
            distances = np.hypot(x - self.xs[event.ind[0]], y - self.ys[event.ind[0]])
            print("distances: ",distances)
            indmin = distances.argmin()
            #print("indmin: ",indmin)
            dataind = event.ind[indmin]
            #print("dataind: ",dataind)
            print("Cumulative Trace Number: ", self.cumulative_trace_number[dataind])
            print("Starttime: ",self.starttime[dataind])
        else: #TODO Make this pick the extraction points and plot them
            print("Extract Mode On!")
        self.lastind = dataind
        self.update()

    def update(self):
        """
        Function to update plot
        """
        if self.lastind is None:
            return
        
        dataind = self.lastind
        
        #if the user has selected any split points, they are plotted 
        if len(self.split) > 0:
            self.split_points.set_visible(True)
            self.split_points.set_data(self.split_x, self.split_y)
        elif len(self.split) == 0:
            self.split_points.set_visible(False)
        
        #updating plot
        self.selected.set_visible(True)
        self.selected.set_data(self.xs[dataind], self.ys[dataind])
        self.text.set_text('{} {} {} \nTrace: {}'.format(self.starttime[dataind].year,self.starttime[dataind].julday,self.starttime[dataind].time.isoformat(),self.traceno[dataind]))# % self.traceno[dataind])# +  + % self.starttime[dataind])
        self.canvas.draw()
    def extract_segy(self):
        """
        Function to extract the segy between two split points, without exporting segys grom the rest of the survey
        
        TODO: not implemented yet!
        """
        if len(self.split) != 2:
            self.statuslbl.setText('Error: Extract function only works when there are 2 splits chosen.')
            return
        #order list of splits from smallest to largest
        self.split = sorted(self.split)
        
        #check if there are any splits that are greater than 32767 traces, if so add artificial splits so that the stream does not have more than 32767 traces (obspy will throw error otherwise)
        temp_splits = [0] + self.split + [len(self.traceno)-1]
        all_splits = insert_required_artificial_splits(temp_splits)
        self.split = all_splits[1:-1]
        
        #replicate self.file_dictionary but fill each keys with whichever splits fall under that file
        #this way both dictionaries have common keys but different information
        self.file_dictionary_splits = {}
        for key in self.file_dictionary.keys():
            self.file_dictionary_splits[key] = []
        
        for i in self.split:
            for key in self.file_dictionary_splits.keys():
                if i >= self.file_dictionary[key][0] and i<= self.file_dictionary[key][-1]:
                    self.file_dictionary_splits[key].append(i)
        
    def get_survey_folder_name(self):
        """
        Handler called when 'Browse' is clicked
        """
        temp_fname = QtWidgets.QFileDialog.getExistingDirectory(self,'Select Input Folder')
        self.fname = str(temp_fname)
        if self.fname is not None:
            self.lbl.setText('Input Folder: ' + self.fname)
        else:
            self.lbl.setText('No folder selected')
    def get_foldername(self):
        """
        Handler called when 'Output Folder' is clicked
        """
        temp_foldername = QtWidgets.QFileDialog.getExistingDirectory(self,'Select Output Folder')
        self.foldername = str(temp_foldername)
        if self.foldername is not None:
            self.lbl2.setText('Output folder: ' + self.foldername)
        else:
            self.lbl2.setText('No file selected')
    def update_progress(self, number):
        """
        Update function for progress bar
        """
        self.completed = number
        self.progress.setValue(self.completed)
    def plotSURVEY(self):
        """
        Plot navigation of all SEG-Y's in input folder
        """
        #check if input file is selected
        if self.fname == None:
            self.statuslbl.setText('Error: No folder selected! Please browse for input folder.')
            return
        if self.foldername == None:
            self.statuslbl.setText('Error: No output folder selected! Please browse for output folder.')
            return
        
        self.statuslbl.setText('Plotting files...')
        self.update_progress(0)
        #creat navlog to write any warnings to
        navlog_path =  self.foldername + '/' + str(self.prefix_box.text()) + '_navlog.txt'
        self.init_navlog(navlog_path)
        
        #make list of the sample intervals for each file
        self.delta_list = []
        
        #make list of segy files being used
        self.segy_list = []
        
        #populate list of segys
        import os
        for file in os.listdir(self.fname):
            
            if file.endswith(".sgy") or file.endswith(".segy"):
                self.segy_list.append(os.path.join(self.fname, file))
        
        if len(self.segy_list) == 0:
            
            self.statuslbl.setText('Error: No SEG-Y files found in that folder.')
            return
        
        #sort segy files by their date modified (#TODO: make this preference change-able. will work for raw segy files straight from Knudsen - may need a more elegant solution for different logging systems/workflows)
        #self.segy_list.sort(key=lambda x: os.path.getmtime(x))
        self.segy_list.sort()
        #create dictionary with each file name and first and last trace of each segy
        self.file_dictionary = {}
        self.dictionary_keys = [] 
        cumulative_trace = 0
        
        #read each of the segys and count the traces
        for i in self.segy_list:
            #break file path up and just take the file name for the dictionary key
            break_file_name = i.split('\\')
            key = break_file_name[-1]
            #make a list of these keys so the order is preserved when they're retrieved during export
            self.dictionary_keys.append(key)
            
            #making a dictionary entry with a list containing first trace number
            if cumulative_trace == 0:
                self.file_dictionary[key] = [cumulative_trace]
            else:
                self.file_dictionary[key] = [cumulative_trace]
                
            #read segy (headers only)
            temp_stream = read(i, unpack_trace_headers = True, headonly = True)
            
            #detect the sample interval of first trace #TODO: not used for anything
            #self.delta_list.append(round(temp_stream[0].stats.delta,7))
            
            for trace in range(len(temp_stream)):
                self.cumulative_trace_number.append(cumulative_trace)
                temp_lon = (temp_stream[trace].stats['segy']['trace_header']['source_coordinate_x'])/3600000.0
                temp_lat = (temp_stream[trace].stats['segy']['trace_header']['source_coordinate_y'])/3600000.0
                #if navigation is missing make an entry in the logfile
                if temp_lon == 0 and temp_lat == 0:
                    self.enter_navlog(navlog_path, 
                                      "Navigation missing" + "," + key + "," + 
                                      str(temp_stream[trace].stats['segy']['trace_header']['trace_sequence_number_within_segy_file']) + "," + 
                                      temp_stream[trace].stats['starttime'].datetime.strftime('%j %H:%M:%S'))
                self.lon.append(temp_lon)
                self.lat.append(temp_lat)
                self.starttime.append(temp_stream[trace].stats['starttime'])
                self.endtime.append(temp_stream[trace].stats['endtime'])
                self.traceno.append(trace)
                cumulative_trace += 1
            self.file_dictionary[key].append(cumulative_trace)
            temp_stream = None
        self.update_progress(50)
        
        #creating local stereographic projection centered on averaged coordinates in line #TODO: make this an edit-able preference
        myProj = Proj(proj = 'stere', ellps = 'WGS84', lon_0 = np.average(self.lon), lat_0 = np.average(self.lat), units = 'm', no_defs = True)
        #OR: Use projection defined by EPSG code
        #myProj = Proj(init='EPSG:3996')
        
        #project coordinates
        for i in range(len(self.lat)):
            x_temp, y_temp = myProj(self.lon[i],self.lat[i])
            self.xs.append(x_temp)
            self.ys.append(y_temp)
        
        #replace zero'd navigation with nan values to prevent matplotlib plot from being skewed
        for i in range(len(self.lat)):
            if self.lat[i] == 0.0 and self.lon[i] == 0.0:
                self.xs[i] = float('nan')
                self.ys[i] = float('nan')
        
        self.ax.set_aspect('equal', 'datalim')
        
        #plot nav
        self.line, = self.ax.plot(self.xs, self.ys, '-', picker=5)
        
        self.update_progress(75)
        
        #connect matplotlib events
        self.canvas.mpl_connect('pick_event', self.onpick)
        self.canvas.mpl_connect('key_press_event', self.onpress)
        self.canvas.mpl_connect('key_press_event', self.splitkeys)
        self.canvas.draw()
        
        self.update_progress(100)
        self.statuslbl.setText('Ready!')
        
    def splitSURVEY(self):
        """
        This is the function called when 'Split Survey' is pressed. It exports SEG-Y files that start and stop using the current splits entered in the program.
        """
        if self.fname == None:
            self.statuslbl.setText('Error: No folder selected! Please browse for input folder.')
            return
        if len(self.split) == 0:
            self.statuslbl.setText('Error: Please specify which trace(s) at which you would like to split')
            return
        if self.foldername == None:
            self.statuslbl.setText('Error: Please specify output folder')
            return
        
        self.update_progress(0)
        
        #order list of splits from smallest to largest
        self.split = sorted(self.split)
        
        #log the splits to a file so they can be reimported
        splits_path = self.foldername + '/' + str(self.prefix_box.text()) +'_splits.split'
        self.output_split_list(splits_path,self.split,self.split_x,self.split_y)
        
        #write log file containing where lines start and stop (SOL, EOL)
        log_path = self.foldername + '/' + str(self.prefix_box.text()) + '_lines.log'
        self.init_logfile(log_path)
        lines = chunks([0] + self.split + [len(self.traceno)-1])
        for i in range(len(lines)):
            linenumber = i
            self.enter_line_in_logfile(log_path, linenumber, lines[i])
        
        #check if there are any splits that are greater than 32767 traces, if so add artificial splits so that the stream does not have more than 32767 traces (obspy will throw error otherwise)
        temp_splits = [0] + self.split + [len(self.traceno)-1]
        all_splits = insert_required_artificial_splits(temp_splits)
        self.split = all_splits[1:-1]
        
        #create a line counter to make it easier to name the output lines in the for loop
        self.line_counter = 0
        
        #replicate self.file_dictionary but fill each keys with whichever splits fall under that file
        #this way both dictionaries have common keys but different information
        self.file_dictionary_splits = {}
        for key in self.file_dictionary.keys():
            self.file_dictionary_splits[key] = []
        
        for i in self.split:
            for key in self.file_dictionary_splits.keys():
                if i > self.file_dictionary[key][0] and i<= self.file_dictionary[key][-1]: #TIP: removed the = from the first >= so that if the split happens right on a file boundary it will only be listed in the first file's dictionary lookup
                    self.file_dictionary_splits[key].append(i)
        
        #create master temporary stream here
        st = Stream()
        
        #for each file in the survey
        for key in self.dictionary_keys:
            #if there are no splits set for this file
            if len(self.file_dictionary_splits[key]) == 0:
                #read segy
                temp = read(self.fname+'/'+key)
                
                #define start and end traces
                start_trace = 0
                end_trace = len(temp) #removed the -1, which fixed the problem of losing the last trace
                
                #for every trace in temporary stream, temp, append it to master stream, st
                for i in temp.traces[start_trace:end_trace]:
                    st.append(i)
                
                #overwrite temporary stream with nulled Stream object
                temp = Stream()
                
            if len(self.file_dictionary_splits[key]) > 0:
                #read segy
                temp = read(self.fname+'/'+key)
                
                #translate split number to one relative to the current file by subtracting the first trace value from the file dictionary
                relative_splits = [x - self.file_dictionary[key][0] for x in self.file_dictionary_splits[key]]

                last_trace_int = len(temp) - 1 
                #generate chunk list/start and end points of each output
                split_integers = chunks([0] + relative_splits + [last_trace_int])
                #print("Chunked split integers: ",split_integers)
                
                #for each chunk...
                for i in split_integers:
                    
                    #if it is the last chunk (i.e. the last number in the chunk corresponds with the last trace in the file)
                    if i[-1] == last_trace_int:
                        print("Starting new master stream...")                        
                        #append to stream but don't output
                        append_chunk_to_master(i, temp, st)
                    #else, append the chunk to the stream and output 
                    else:
                        print("Outputting stream to master and outputting file...")
                        print("Output Master String Length: ",len(st))
                        
                        #create a text string to define what line this belongs to (does not consider automatic splits)
                        line_test_integer = i[-1] + self.file_dictionary[key][0]
                        line_number_text = None
                        self.line_counter = 0
                        for line in lines:
                            self.line_counter += 1
                            if line_test_integer > line[0] and line_test_integer <= line[-1]:
                                line_number_text = 'line' + str(self.line_counter).zfill(3)
                        
                        append_chunk_to_master(i,temp,st)
                        
                        output_master_stream(st, output_folder = self.foldername, cruise_id_text = str(self.prefix_box.text()), suffix = line_number_text)
                        
                        #clear master stream
                        st = Stream()
                #clear temporary stream
                temp = Stream()
        #if there is any data left over in the master stream at the end of the survey, output it to segy
        if len(st) > 0:
            #TODO: clean up line naming here, it currently works because self.line_counter is already at it max from the for loop above, but there is probably a better way to do this with a function
            line_number_text = 'line' + str(self.line_counter).zfill(3)
            output_master_stream(st, output_folder = self.foldername, cruise_id_text = str(self.prefix_box.text()), suffix = line_number_text)

if __name__ == '__main__':
    
    app = QtWidgets.QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())
