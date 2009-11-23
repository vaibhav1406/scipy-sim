'''
Created on 19/11/2009

@author: brian
'''
try:
    import queue
except ImportError:
    import Queue as queue
    
import threading

import numpy

import logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Logger enabled")

import signal   # If we inport signal we can kill the program with Ctrl C

gui_lock = threading.Condition()

"""
Notes
q = queue.Queue(0) # creates a new unbounded thread-safe fifo queue (which we can use for our Kahn Network)

q.put(item,block=False) # Non-Blocking add (can have a timeout or block if reqd) Will throw "Full" if somehow we run out of memory

"""


class Actor(threading.Thread):
    '''
    This is a base Actor class for use in a simulation
    '''  
    def __init__(self, input_queue=None, output_queue=None):
        '''
        Constructor for an actor
        '''
        threading.Thread.__init__(self)
        logging.debug("Constructing a new Actor thread")
        
        # Every actor will have an input thread - even if its just a control
        if input_queue is None:
            input_queue = queue.Queue(0)
        self.input_queue = input_queue
        
        # Don't require an output queue
        self.output_queue = output_queue
        
        self.stop = False
        self.setDaemon(True)
    
        
    def run(self):
        '''
        Run this actor objects thread
        '''
        logging.debug("Started running an actor thread")
        while not self.stop:
            logging.debug("Processing now")
            self.process()
    
    def process(self):
        raise NotImplementedError("This base class is supposed to be derived from")

import time
import matplotlib
#matplotlib.use('TkAgg') # do this before importing pylab

import matplotlib.pyplot as plt


class Plotter(Actor):
    '''
    This actor shows a signal...
    '''
    
    def __init__(self, input):
        Actor.__init__(self, input_queue=input)
        self.x = []
        self.y = []
        plt.ion()
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
        
        obj = self.input_queue.get()     # this is blocking...
        if obj is None:
            self.stop = True
            return
        self.x.append(obj['tag'])
        self.y.append(obj['value'])
        logging.debug("Plotter received values ( %e,%e ) Now have %i values" % (self.y[-1], self.x[-1], len(self.x)))
        obj = None
        
        # Probably don't want to plot every change!
        self.update_plot()


    def update_plot(self):
        logging.debug("Updating plot refresh:%i" % self.refreshs)
        if self.refreshs >= 1000:
            self.stop = True
            return
        self.refreshs += 1
        
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
        

class Ramp(Actor):
    '''
    This actor is a ramp source
    '''
    
    def __init__(self, out, amplitude=2.0, freq=1.0/30, res=10):
        """
        default params creates a ramp up to 2 that takes 30 seconds with 10 values per "second"
        
        """
        Actor.__init__(self, output_queue=out)
        self.amplitude = amplitude
        self.frequency = freq
        self.resolution = res
    
    def process(self):
        """Create the numbers..."""
        logging.debug("Running ramp process")
        tags = numpy.linspace(0, 120, 120*self.resolution)  # for now just compute 2 minutes of values
        
        for tag in tags:
            
                
            value = tag * self.frequency * self.amplitude
            
            while value >= self.amplitude:
                value = value - self.amplitude
            
            data = {
                    "tag": tag,
                    "value": value
                    }
            self.output_queue.put(data)
        self.stop = True
        
        
   
if __name__ == "__main__":
    connection = queue.Queue(0)
    src = Ramp(connection)
    dst = Plotter(connection)
    
    components = [src, dst]
    
    logging.info("Starting simulation")
    for component in components:
        component.start()
    logging.debug("Finished starting actors")
    
    
    src.join()
    
    
    plt.show()
    dst.join()
    logging.debug("Finished running actor")
