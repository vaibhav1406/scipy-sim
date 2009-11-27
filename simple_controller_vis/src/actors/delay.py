'''
Created on 23/11/2009

@author: Brian Thorne
'''

import logging
import numpy
from Actor import Source, Actor

try:
    import queue
except ImportError:
    import Queue as queue
    
import time, random # These are used to test the async

class Delay(Actor):
    '''
    This actor takes a source and delays it by an arbitrary amount of time.
    '''
    
    def __init__(self, input, out, wait=1.0):
        """
        default to delaying the signal by one second.
        """
        Actor.__init__(self, input_queue=input, output_queue=out)
        
        self.delay = wait
    
    def process(self):
        """Delay the input values by a set amount of time..."""
        logging.debug("Running delay process")
        
        obj = self.input_queue.get(True)     # this is blocking
        if obj is None:
            logging.info("We have finished delaying the data")
            self.stop = True
            self.output_queue.put(None)
            return
        tag =  obj['tag'] + self.delay
        value = obj['value']
        data = {
            "tag": tag,
            "value": value
            }
        self.output_queue.put(data)
        obj = None
        
