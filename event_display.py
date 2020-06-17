#!/usr/bin/python3
# You may need to change above...  !/usr/bin/python
# it is set for my MacOS machine
#
# event display using tkinter.
#
# Usage:
#   event_display.py input_event_data.npz input_geometry.npz
#
# features:
# buttons: 1) Charge display
#          2) Time display
#          3) QT display
#          4) Update
#          5) Next event
#          6) Prev event
# text inputs: 1) minimum value in display
#              2) maximum value in display
#              3) set event number
# 
#
# Authors:  Blair Jamieson,  Connor Boubard
# Date: June 2020
#

import tkinter as tk
from tkinter import ttk
from mpl_toolkits.mplot3d import Axes3D

import matplotlib 
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import numpy as np
import math
import sys

import argparse

def get_args():
    """
    Command line arguments to the python script
    """
    parser = argparse.ArgumentParser(description='Display IWCD events from npz files (geometry-file and event-file)')
    parser.add_argument('geometry_file', type=str, default=None, nargs='?')
    parser.add_argument('event_file', type=str, default=None, nargs='?')
    parser.add_argument('event', type=int, default=0, nargs='?')
    args = parser.parse_args()
    return args


class EventDisplayWindow( tk.Tk ):
    """
    Main tkinter window to select among the different frames.
    """
    
    def __init__( self, *args, **kwargs ):
        """
        Initialize the different frames that can be displayed (Charge, Time, or Charge vs Time)
        """
        tk.Tk.__init__( self, *args, **kwargs )
        tk.Tk.wm_title( self, "IWCD npz file Event Display" )

        self.main_window = tk.Frame( self )
        self.main_window.pack(side="top", fill="both", expand = True )
        self.main_window.grid_rowconfigure(0, weight=1)
        self.main_window.grid_columnconfigure(0, weight=1)

        self.windows = {}

        for win in ( ChargeDisplay, TimeDisplay, QTDisplay ):
            window = win( self.main_window, self )
            self.windows[ win ] = window
            window.grid( row=0, column=0, sticky="nsew"  )

        self.show_window( ChargeDisplay )


    def show_window( self, win ):
        """
        Selects which frame to display on top
        """
        window = self.windows[ win ]
        window.update_plot()
        window.tkraise()

    def quit( self ):
        """
        Quit program. Couldn't get it to cleanup properly, so just did kludge sys.exit()
        """
        for win in self.windows:
            self.windows[ win ].destroy()
        self.main_window.destroy()
        self.destroy()
        print("Goodbye.")
        sys.exit()



def EvDispNavigation( self_frame, main_frame, zrange ):
    """
    Function to return a frame holding all the  navigation buttons.
    self_frame is the frame that the button frame will be added to.
    main_frame is the frame that selects which frame to put on top
    zrange is setting for z axis range [-1,-1] to autorange
    """
    global event_number
    global num_events
    frm = tk.Frame( self_frame )
    # buttons to change which plot
    btn_qdisp = ttk.Button( frm, text = "Q", command = lambda: main_frame.show_window( ChargeDisplay ) )
    btn_tdisp = ttk.Button( frm, text = "T", command = lambda: main_frame.show_window( TimeDisplay ) )
    btn_qtdisp = ttk.Button( frm, text = "QT", command = lambda: main_frame.show_window( QTDisplay ) )
    btn_qdisp.pack(side=tk.LEFT)
    btn_tdisp.pack(side=tk.LEFT)
    btn_qtdisp.pack(side=tk.LEFT)

    # current event displayed
    lbl_evno = ttk.Label( frm, text="Event: " )
    lbl_evno.pack(side=tk.LEFT)
    entry_evno = ttk.Entry( frm, width=10 )
    entry_evno.insert( 0, str( event_number ) )
    entry_evno.pack(side=tk.LEFT)
    lbl_numev = ttk.Label( frm, text=" / "+str(num_events) )
    lbl_numev.pack(side=tk.LEFT)
    
    # next event button
    btn_nextev = ttk.Button( frm, text = "Next Event", command = lambda: GetNextEvent( self_frame, entry_evno ) )
    btn_nextev.pack(side=tk.LEFT)

    # zaxis range
    lbl_zmin = ttk.Label( frm, text="zmin: " )
    lbl_zmin.pack(side=tk.LEFT)
    entry_zmin = ttk.Entry( frm, width=10 )
    entry_zmin.insert( 0, str( zrange[0] ) )
    entry_zmin.pack(side=tk.LEFT)

    lbl_zmax = ttk.Label( frm, text="zmax: " )
    lbl_zmax.pack(side=tk.LEFT)
    entry_zmax = ttk.Entry( frm, width=10 )
    entry_zmax.insert( 0, str( zrange[1] ) )
    entry_zmax.pack(side=tk.LEFT)

    # apply axis range button
    btn_apply = ttk.Button( frm, text = "Apply zrange", command = lambda: ApplyZrange( self_frame, entry_zmin, entry_zmax ) )
    btn_apply.pack(side=tk.LEFT)

    # quit button
    btn_quit = ttk.Button( frm, text = "Quit", command = lambda: main_frame.quit() )
    btn_quit.pack(side=tk.LEFT)
    
    return frm

        

class ChargeDisplay( tk.Frame ):
    """
    Frame to hold the charge event display.
    """
    global event_number
    def __init__( self, parent, main_win ):
        tk.Frame.__init__( self, parent )
        self.main_window = main_win
        self.make_plot()

    def update_plot(self, zrange=[-1.,-1.] ):
        """
        update_plot deletes the existing button frame, toolbar, and plot, 
        and builds a fresh plot by calling make_plot
        """
        plt.close( self.fig )
        self.frm_plot.destroy()
        self.frm_buttons.destroy()
        self.toolbar.destroy()
        self.make_plot(zrange)
        
    def make_plot(self, zrange=[-1.,-1.] ):
        """
        makes the button frame, and charge display frame, and makes the charge plot
        """
        self.frm_buttons = EvDispNavigation( self, self.main_window, zrange )
        self.frm_buttons.pack()
        
        self.frm_plot = tk.Frame( self )        
        self.fig = EventDisplay( digitubes, digicharges, "Charges for event "+str(event_number), zrange )
        canvas = FigureCanvasTkAgg( self.fig, self.frm_plot )
        canvas.draw()
        canvas.get_tk_widget().pack( side=tk.BOTTOM, fill=tk.BOTH, expand = True )

        self.toolbar = NavigationToolbar2Tk( canvas, self )
        self.toolbar.update()
        canvas._tkcanvas.pack( side=tk.TOP, fill=tk.BOTH, expand=True )
        self.frm_plot.pack()
        
        
    
class TimeDisplay( tk.Frame ):
    """
    Frame to hold the time event display.
    """
    global event_number
    def __init__( self, parent, main_win ):
        tk.Frame.__init__( self, parent )
        self.main_window = main_win
        self.make_plot()

    def update_plot(self, zrange=[-1.,1.] ):
        """
        update_plot deletes the existing button frame, toolbar, and plot, 
        and builds a fresh plot by calling make_plot
        """
        plt.close( self.fig )
        self.frm_plot.destroy()
        self.frm_buttons.destroy()
        self.toolbar.destroy()
        self.make_plot(zrange)

    def make_plot(self,zrange=[-1.,1.] ):
        """
        makes the button frame, time display frame, and makes the time plot
        """
        self.frm_buttons = EvDispNavigation( self, self.main_window, zrange )
        self.frm_buttons.pack()

        self.frm_plot = tk.Frame( self )
        self.fig = EventDisplay( digitubes, digitimes, "Times for event "+str(event_number), zrange )
        canvas = FigureCanvasTkAgg( self.fig, self.frm_plot )
        canvas.draw()
        canvas.get_tk_widget().pack( side = tk.BOTTOM, fill=tk.BOTH, expand = True )

        self.toolbar = NavigationToolbar2Tk( canvas, self )
        self.toolbar.update()
        canvas._tkcanvas.pack( side=tk.TOP, fill=tk.BOTH, expand=True )
        self.frm_plot.pack()

            
class QTDisplay( tk.Frame ):
    """
    Frame to hold the charge versus time event display.
    """
    global event_number
    def __init__( self, parent, main_win ):
        tk.Frame.__init__( self, parent )
        self.main_window = main_win
        self.make_plot()
        
    def update_plot(self, zrange=[-1.,-1.]):
        """
        update_plot deletes the existing button frame, toolbar, and plot, 
        and builds a fresh plot by calling make_plot
        """
        plt.close( self.fig )
        self.frm_plot.destroy()
        self.frm_buttons.destroy()
        self.toolbar.destroy()
        self.make_plot(zrange)

    def make_plot(self, zrange=[-1.,-1.]):
        """
        makes the button frame, charge vs time display frame, and makes the charge vs time plot
        """
        self.frm_buttons = EvDispNavigation( self, self.main_window, zrange )
        self.frm_buttons.pack()
        
        self.frm_plot = tk.Frame( self )
        self.fig = ChargeTimeHist( digitimes, digicharges, "Q vs T for event "+str(event_number) )
        canvas = FigureCanvasTkAgg( self.fig, self.frm_plot )
        canvas.draw()
        canvas.get_tk_widget().pack( side = tk.TOP, fill=tk.BOTH, expand = True )

        self.toolbar = NavigationToolbar2Tk( canvas, self )
        self.toolbar.update()
        canvas._tkcanvas.pack( side=tk.TOP, fill=tk.BOTH, expand=True )
        self.frm_plot.pack()
        



def PMT_to_flat_cylinder_map_positive( tubes, tube_xyz ):
    """
    Build dictionary of PMT number, to (x,y) on a flat cylinder
    
    N.B. Tube numbers in full geometry file go from 1:NPMTs, but it seems like
    the event data number from 0:NPMTs-1, so subtracting 1 from tube number here?
    
    """
    mapping = {}
    for idx, tube in enumerate(tubes):
        x = tube_xyz[idx,0]
        y = tube_xyz[idx,1]
        z = tube_xyz[idx,2]
        if ( y > 500. ):
            # in top circle of cylinder
            xflat = x+1162.7
            yflat = 2165.2 + z
            mapping[ int( tube-1 ) ] = [ int(round(xflat)), int(round(yflat)) ]
            
        elif ( y < -500.):
            # in bottom circle of cylinder
            xflat = x+1162.7
            yflat = 370.1 + z
            mapping[ int( tube-1 ) ] = [ int(round(xflat)), int(round(yflat)) ]
            
        else:
            # in barrel part of cylinder
            theta = math.atan2( z, x )
            xflat = R * theta + 1162.7
            yflat = y + 1267.7
            mapping[ int( tube-1 ) ] = [ int(round(xflat)), int(round(yflat)) ]
    return mapping

def EventDisplay( tubes, quantities, title="Charge", cutrange=[-1,-1] ):
    """
    tubes == np.array of PMTs that were hit
    quantities == np.array of PMT quantities (either charge or time)
    title == title to add to display
    cutrange == minimum and maximum values on plot (or set both same for default)
    """
    
    fig = plt.figure(figsize=[10,8]) 
    preimage = np.zeros( [2506, 2317] )
    imgmin = quantities.min()
    imgmax = quantities.max()
    for idx, tube in enumerate( tubes ):
        if cutrange[0] != cutrange[1]:
            if quantities[idx] < cutrange[0] or quantities[idx] > cutrange[1]:
                continue
        for dx in range(-3,4):
            for dy in range(-3,4):
                if abs(dx)==3 and abs(dy)==3:
                    continue
                    
                #print( "idx=", idx, " len(quantities)=",len(quantities), " tube=", tube, " len(PMTFlatMap)=", len(PMTFlatMapPositive))
                preimage[ PMTFlatMapPositive[tube][1]+dx, PMTFlatMapPositive[tube][0]+dy ] = quantities[idx]

    if cutrange[0] != cutrange[1]:
        imgmin = cutrange[0]
        imgmax = cutrange[1]
    plt.imshow( preimage, extent = [-1162.7,1162.7,-1267.7,1267.7], vmin=imgmin, vmax=imgmax )
    fig.suptitle(title, fontsize=20)
    plt.xlabel('Distance CCW on perimeter from x-axis (cm)', fontsize=18)
    plt.ylabel('Y (cm)', fontsize=16)
    plt.set_cmap('cubehelix_r')
    plt.colorbar()
    return fig
    

def ChargeTimeHist( times, charges, title='Event Charge versus Time', cutrange = [[-1,-1],[-1,-1]] ):
    """
    Makes a 2d histogram of charge versus time.
    inputs:
    times is an np.array of times of PMT hits
    charges is an np.array of charges of PMT hits
    title is the title of the histogram
    cutrange has two ranges, one in x and one in y [ [tmin, tmax], [qmin,qmax] ]
    """
    fig = plt.figure(figsize=[10,8]) 
    tmin = times.min()
    tmax = times.max()
    qmin = charges.min()
    qmax = charges.max()

    if cutrange[0][0] != cutrange[0][1]:
        tmin = cutrange[0][0]
        tmax = cutrange[0][1]
    if cutrange[1][0] != cutrange[1][1]:
        qmin = cutrange[1][0]
        qmax = cutrange[1][1]
        
    plt.hist2d( times, charges, [100,100], [[tmin,tmax],[qmin,qmax]] )
    fig.suptitle(title, fontsize=20)
    plt.xlabel('Time (ns)', fontsize=18)
    plt.ylabel('Charge (pe)', fontsize=16)
    plt.set_cmap('cubehelix_r')
    plt.colorbar()
    return fig


def GetNextEvent( self_frame, entry_ev ):
    """
    Load the next event, and update the current frame's plot with the current event
    Inputs are the frame to update, and the tk.Entry that holds the event number
    """
    global event_number
    global digitubes
    global digicharges
    global digitimes

    print("GetNextEvent: current= ",event_number)
    event = int( entry_ev.get() )
    if event != event_number and event+1 < num_events:
        event_number = event-1


    if event_number+1 < num_events:
        event_number += 1
        print("GetNextEvent: loading= ",event_number)

        digitubes = datafile[ 'digi_hit_pmt' ][ event_number ]
        digicharges = datafile[ 'digi_hit_charge' ][ event_number ]
        digitimes = datafile[ 'digi_hit_time' ][ event_number ]
        self_frame.update_plot() 
    else:
        print("At end of file, no more events to load.")

def ApplyZrange( self_frame, entry_zmin, entry_zmax ):
    """
    Read the tk.Entry for the zmin and zmax values to set on the plot for the current frame.
    Ignores the QTDisplay frame, since the builder function for that plot doesn't have a z-axis scaling option.
    """
    if self_frame == QTDisplay:
        print("Z axis not scalable for QTDisplay")
        return
    zmin = float( entry_zmin.get() )
    zmax = float( entry_zmax.get() )
    print("zmin=",zmin," zmax=",zmax )
    self_frame.update_plot( [zmin, zmax] )
    

if __name__ == '__main__':
    root = tk.Tk()        
    config = get_args()
    event_number = config.event
    geofilename = config.geometry_file
    eventfilename = config.event_file
    
    if geofilename is None:
        geofilename =  tk.filedialog.askopenfilename(initialdir = "./",title = "Select geometry file",filetypes = (("npz files","*.npz"),("all files","*.*")))

    if eventfilename is None:
        eventfilename =  tk.filedialog.askopenfilename(initialdir = "./",title = "Select event file",filetypes = (("npz files","*.npz"),("all files","*.*")))

    print ( "Event file is : ", eventfilename )
    print ( "Geometry file is : ", geofilename )

    root.destroy()

    datafile = np.load( eventfilename, allow_pickle=True )
    #'IWCDmPMT_4pi_full_tank_mu-_E0to1000MeV_unif-pos-R371-y521cm_4pi-dir_3000evts_25.npz',allow_pickle=True)
    geofile = np.load( geofilename, allow_pickle=True )
    #'full_geo_dump.npz',allow_pickle=True)

    tubes = geofile[ 'tube_no' ]
    tube_xyz = geofile[ 'position' ]
    tube_x = tube_xyz[:,0]
    R =  (tube_x.max() - tube_x.min())/2.0
    print("R=",R)

    PMTFlatMapPositive = PMT_to_flat_cylinder_map_positive( tubes, tube_xyz )

    num_events = len( datafile[ 'digi_hit_pmt' ] )
    if event_number >= num_events:
        print("Requested event is beyond number of events in file")
        event_number = num_events-1
        print("Set event number to ",event_number)
    
    digitubes = datafile[ 'digi_hit_pmt' ][ event_number ]
    digicharges = datafile[ 'digi_hit_charge' ][ event_number ]
    digitimes = datafile[ 'digi_hit_time' ][ event_number ]



    app = EventDisplayWindow()
    app.mainloop()

