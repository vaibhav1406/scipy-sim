'''
This dynamic plotter shows a live signal stream.
'''

from Actor import Actor
import matplotlib.pyplot as plt
import logging
try:
    import queue
except ImportError:
    import Queue as queue

import threading
gui_lock = threading.Condition()

import time

class Plotter(Actor):
    '''
    This actor shows a signal dynamically as it comes off the buffer with matplotlib.
    The max refresh rate is an optional input - default is 10Hz
    '''
    
    def __init__(self, input, refresh_rate=10):
        Actor.__init__(self, input_queue=input)
        self.x = []
        self.y = []
        assert refresh_rate != 0
        self.refresh_rate = refresh_rate
        plt.ion()
        self.line, = plt.plot(self.x, self.y)   #, animated=True, lw=2)
        self.refreshs = 0
        self.updatePlot = True
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

        self.x.append(obj['tag'])
        self.y.append(obj['value'])
        logging.debug("Plotter received values ( %e,%e ) Now have %i values." % (self.y[-1], self.x[-1], len(self.x)))
        obj = None
        
        if time.time() - self.last_update > 1.0/self.refresh_rate:
            self.update_plot()


    def update_plot(self):
        logging.debug("Updating plot (refresh: %i)" % self.refreshs)
        self.last_update = time.time()
        if self.refreshs >= 1000:
            logging.info("We have updated the plot 1000 times - forcing a stop of the simulation now")
            self.stop = True
            return
        self.refreshs += 1
        
        with gui_lock:
            self.line.set_data(self.x, self.y)
            ax = self.line.get_axes()
            self.line.recache()
            ax.relim()
            ax.autoscale_view()
            plt.draw() # redraw the canvas
        
        # It might prove to be beneficial just to redraw small bits 
        # just redraw the axes rectangle
        #self.fig.canvas.blit(self.ax.bbox)
        #self.fig.canvas.draw()
        #self.fig.canvas.manager.window.after(100, self.update_plot)
        

