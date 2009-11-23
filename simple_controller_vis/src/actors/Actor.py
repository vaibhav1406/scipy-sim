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

import time, random # These are used to test the async

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
            #logging.debug("Some actor is processing now")
            self.process()
    
    def process(self):
        raise NotImplementedError("This base class is supposed to be derived from")

import time
import matplotlib
#matplotlib.use('TkAgg') # do this before importing pylab

import matplotlib.pyplot as plt
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
        

class Ramp(Actor):
    '''
    This actor is a ramp source
    '''
    
    def __init__(self, out, amplitude=2.0, freq=1.0/30, res=10):
        """
        default parameters creates a ramp up to 2 that takes 30 seconds with 10 values per "second"
        
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
            logging.debug("Ramp process added data: (tag: %2.e, value: %.2e)" % (tag, value))
            time.sleep(random.random() * 0.001)
        logging.debug("Ramp process finished adding all data to queue")    
        self.stop = True
        self.output_queue.put(None)
        
        
   
if __name__ == "__main__":
    connection = queue.Queue(0)
    src = Ramp(connection)
    dst = Plotter(connection)
    
    components = [src, dst]
    
    logging.info("Starting simulation")
    for component in components:
        component.start()
    logging.debug("Finished starting actors")
    
    
    
    
    
    plt.show()   # The program will stay "running" while this plot is open
    
    src.join()
    dst.join()
    
    logging.debug("Finished running actor")
