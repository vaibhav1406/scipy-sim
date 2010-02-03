'''
This dynamic plotter shows a live signal stream.
'''

from scipysim.actors import DisplayActor
import matplotlib.pyplot as plt
import logging
import threading

GUI_LOCK = threading.Condition()

import time

class Plotter(DisplayActor):
    '''
    This actor shows a signal dynamically as it comes off the buffer with matplotlib.
    The max refresh rate is an optional input - default is 1/2Hz
    '''
    active_plots = 0
    def __init__(self, input_queue, refresh_rate=0.5):
        super(Plotter, self).__init__(input_queue=input_queue)
        Plotter.active_plots += 1 
        self.x_axis_data = []
        self.y_axis_data = []
        assert refresh_rate != 0
        self.refresh_rate = refresh_rate
        self.min_refresh_time =  1.0 / self.refresh_rate
        plt.ion()
        
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.title = self.ax.set_title('Scipy Simulator Dynamic Plot') 
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
            plt.ioff()
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

        with GUI_LOCK:
            self.line.set_data(self.x_axis_data, self.y_axis_data)
            axes = self.line.get_axes()
            self.line.recache()
            axes.relim()
            axes.autoscale_view()
            plt.draw() # redraw the canvas

        # It might prove to be beneficial just to redraw small bits
        # just redraw the axes rectangle
        #self.fig.canvas.blit(self.ax.bbox)
        #self.fig.canvas.draw()
        #self.fig.canvas.manager.window.after(100, self.update_plot)


