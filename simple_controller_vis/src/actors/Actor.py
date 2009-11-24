'''
Created on 19/11/2009

@author: brian
'''
try:
    import queue
except ImportError:
    import Queue as queue
    
import threading



import logging


#import signal   # If we import signal we can kill the program with Ctrl C



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
        
        # Every actor will have at least an input thread - even if its just a control
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

class Source(Actor):
    '''
    This is just an abstract interface for a signal source.
    Requires an output queue.
    '''

    def __init__(self):
        raise NotImplementedError("This base class is supposed to be derived from")

        
   
if __name__ == "__main__":
    pass
