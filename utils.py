# -*- coding: utf-8 -*-
"""
Created on Sat Sep 22 22:02:57 2018

Some general functions used by the main Window class.

@author: kb
"""
import numpy as np
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

def chunks(l):
    """
    Returns successive pairs in a list l
    """
    output_list = []
    for i in range(0, len(l)):
        if i == 0:
            output_list.append([l[i],l[i+1]])
        if i not in (0, len(l) - 1):
            trace_after_split = l[i] + 1
            output_list.append([trace_after_split, l[i+1]])
        if i == len(l) - 1:
            return output_list

def append_chunk_to_master(chunk, temp, st):
    """
    Appends the passed section of the temporary stream to the master stream.
    """
    #define first and last trace from input chunked list
    start_trace = chunk[0]
    end_trace = chunk[-1] + 1 #This +1 has to do with how python extracts from list, the last number is NOT included in the range

    #append it to master
    for tr in temp.traces[start_trace:end_trace]:
        st.append(tr)

def output_master_stream(st, output_folder = None, cruise_id_text = None, suffix = None):
    """
    Outputs the master stream to SEGY
    """
    #make all the data 32 bit float for segy export
    for tr in st:
        #float imprecision was causing an issue in obspy export for data with a sample rate of 60 ms, so this is a patch solution
        if int(round(tr.stats.delta,7)*1000000) == 60:
            tr.stats['segy']['trace_header']['sample_interval_in_ms_for_this_trace'] = 60 
            tr.stats.sampling_rate = 16666.666666666666
        tr.data = np.require(tr.data, dtype=np.float32)
        
    #get start and end time strings of master stream
    start_time = st.traces[0].stats['starttime']
    start_time_string = start_time.strftime('%j_%H%M')
    end_time = st.traces[-1].stats['endtime']
    end_time_string = end_time.strftime('%j_%H%M')
    
    print("Output starttime: ", start_time_string)
    print("Output endtime: ", end_time_string)
    
    #TODO: fix this - something was giving a None type
    if start_time_string == None:
        start_time_string = ''
    if end_time_string == None:
        end_time_string = ''
    if suffix == None:
        suffix = ''
    
    output_file_path = output_folder + '\\' + cruise_id_text + '_' + start_time_string + '_to_' + end_time_string + '_' + suffix + '.sgy'
    st.write(output_file_path, format='SEGY')

def insert_required_artificial_splits(input_list):
    '''
    This is a function that adds automatic splits when the lines are really long (>26000 traces).
    This is a bit of a band-aid solution to solve errors encountered when exporting large SEG-Y files. 
    There may be a better solution to this.
    '''
    new_list = []
    for i in range(len(input_list)):
        if i>0 and (input_list[i]-input_list[i-1])>26000: #TIP: 26000 has been used instead of 32766 because it still throws an error when the number is that high. This also typically limits the size of the output SEGY to <2 Gb, making them more manageable to work with in other software
            #calculate number of artificial splits needed, and create list with those traces
            n = (input_list[i] - input_list[i-1])//26000
            integer_list = np.linspace(1,n,n,dtype=int)
            inserted_splits = [(input_list[i-1]+x*26000) for x in integer_list]
            new_list.extend(inserted_splits)
            new_list.append(input_list[i])
            print(new_list)
        else:
            new_list.append(input_list[i])
    return new_list

class CustomToolbar(NavigationToolbar):
    
    def __init__(self,canvas_,parent_):
            # list of toolitems to add to the toolbar, format is:
            # (
            #   text, # the text of the button (often not visible to users)
            #   tooltip_text, # the tooltip shown on hover (where possible)
            #   image_file, # name of the image for the button (without the extension)
            #   name_of_method, # name of the method in NavigationToolbar2 to call
            # )
        self.toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Back', 'Back to  previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
        ('Settings', 'Change file I/O preferences', 'Settings', 'settings_nav')
      )
        NavigationToolbar.__init__(self,canvas_,parent_)
        
    def settings_nav(self):
        #settings_function $TODO: not implemented yet!
        print('Settings')
