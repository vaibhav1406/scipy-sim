'''
This dynamic plotter shows a live signal stream.

An alternative to using the queue infrastructure would be 
to "monitor" a variable - http://simpy.sourceforge.net/_build/Recipes/Recipe002.html
'''

from scipysim.actors import DisplayActor

import matplotlib
matplotlib.use('TkAgg')
#from matplotlib.backends.backend_tkagg import FigureCanvasAgg as FigureCanvas
#from matplotlib.figure import Figure

from matplotlib import pyplot as plt

import logging
import threading

GUI_LOCK = threading.Condition()

import time

class Plotter(DisplayActor):
    '''
    This actor shows a signal dynamically as it comes off the buffer with matplotlib.
    The max refresh rate is an optional input - default is 2Hz
    '''
    
    additional_figures = 0
    
    # This was a class attrib is broken on tk8.5/matplotlib.99?
    # Works on osx tk8.4
    #fig = Figure()
    fig = plt.figure()
    #canvas = FigureCanvas(fig)
    
    def __init__(self, 
                 input_queue, 
                 refresh_rate=2, 
                 title='Scipy Simulator Dynamic Plot',
                 own_fig=False):
        super(Plotter, self).__init__(input_queue=input_queue)
        self.x_axis_data = []
        self.y_axis_data = []
        assert refresh_rate != 0
        self.refresh_rate = refresh_rate
        self.min_refresh_time =  1.0 / self.refresh_rate
        
        plt.ioff() # Only draw when we say
        assert plt.isinteractive() == False
        
        self.fig_num = self.additional_figures
        if own_fig:
            Plotter.additional_figures += 1 
            with GUI_LOCK:
                fig = self.myfig = plt.figure()
        else:
            fig = self.fig
        
        self.ax = fig.add_subplot(1,1,1)
        self.title = self.ax.set_title(title) 
        self.line, = self.ax.plot(self.x_axis_data, self.y_axis_data)
        self.refreshs = 0

        self.last_update = 0

    def process(self):
        '''
        plot any values in the buffer
        '''
        obj = self.input_queue.get(True)     # this is blocking
        if obj is None:
            logging.info("We have finished processing the queue of data to be displayed")
            self.update_plot()
            self.stop = True
            return

        self.x_axis_data.append(obj['tag'])
        self.y_axis_data.append(obj['value'])
        #logging.debug("Plotter received values ( %e,%e ) Now have %i values." % (self.y_axis_data[-1], self.x_axis_data[-1], len(self.x_axis_data)))
        obj = None

        if time.time() - self.last_update > self.min_refresh_time:
            self.update_plot()


    def update_plot(self):
        '''
        Update the internal data stored by matplotlib and cause a redraw.
        If this has been called more than 1000 times -> quit.
        '''
        logging.debug("Updating plot (refresh: %i)" % self.refreshs)
        self.last_update = time.time()

        # This is a safety check - if we are plotting over a long time period this needs removing
        if self.refreshs >= 1000:
            logging.warning("We have updated the plot 1000 times - forcing a stop of the simulation now")
            self.stop = True
            return
        self.refreshs += 1

        self.line.set_data(self.x_axis_data, self.y_axis_data)
        axes = self.line.get_axes()
        self.line.recache()
        axes.relim()
        axes.autoscale_view()
        
        with GUI_LOCK:
            # At this point we are 100% sure the main Tk loop has started
            # but for multiple figures we cannot "draw"???
            if self.additional_figures == 0:
                plt.draw()

        # It might prove to be beneficial just to redraw small bits
        # just redraw the axes rectangle
        #self.fig.canvas.blit(self.ax.bbox)
        #self.fig.canvas.draw()
        #self.fig.canvas.manager.window.after(100, self.update_plot)


