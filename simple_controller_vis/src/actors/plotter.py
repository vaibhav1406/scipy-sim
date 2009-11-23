'''
Created on 23/11/2009

@author: brian
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

class Plotter(Actor):
    '''
    This actor shows a signal dynamically as it comes off the buffer with matplotlib.
    '''
    
    def __init__(self, input):
        Actor.__init__(self, input_queue=input)
        self.x = []
        self.y = []
        plt.ion()
        #plt.ioff()
        #self.fig = plt.figure()
        #self.ax = self.fig.add_subplot(111)
        #self.ax.xaxis.set_animated(True)
        #self.ax.yaxis.set_animated(True)
        self.line, = plt.plot(self.x, self.y)#, animated=True, lw=2)
        self.refreshs = 0
        #self.fig.canvas.manager.window.after(1, self.update_plot)
        #self.ax.set_xlim(0,120)
        #self.ax.set_ylim(-1,1)
        
    def process(self):
        '''
        plot any values in the buffer
        '''
        self.updatePlot = False
        
        try:
            while(True):    # Really this is until exception gets raised by an empty queue
                obj = self.input_queue.get(False)     # this is blocking if True... if program is finished... this sucks
                if obj is None:
                    logging.info("We have finished processing the queue of data to be displayed")
                    self.update_plot()
                    self.stop = True
                    return
                self.updatePlot = True
                self.x.append(obj['tag'])
                self.y.append(obj['value'])
                logging.debug("Plotter received values ( %e,%e ) Now have %i values." % (self.y[-1], self.x[-1], len(self.x)))
                obj = None
        except queue.Empty:
            pass
        
        # Don't want to plot every change!
        if self.updatePlot: self.update_plot()


    def update_plot(self):
        logging.debug("Updating plot (refresh: %i)" % self.refreshs)
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
        with gui_lock:
            plt.draw()   # redraw the canvas
        # It might prove to be beneficial just to redraw small bits 
        # just redraw the axes rectangle
        #self.fig.canvas.blit(self.ax.bbox)
        #self.fig.canvas.draw()
        #self.fig.canvas.manager.window.after(100, self.update_plot)
        

