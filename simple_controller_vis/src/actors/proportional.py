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

class Proportional(Source):
    '''
    This actor takes a source and multiplies it by some gain P.
    '''
    
    def __init__(self, input, out, gain=2.0):
        """
        default to doubling the signal
        """
        Actor.__init__(self, input_queue=input, output_queue=out)
        
        self.gain = gain
    
    def process(self):
        """Multiply the input values by a gain..."""
        logging.debug("Running proportional process")
        
        obj = self.input_queue.get(True)     # this is blocking
        if obj is None:
            logging.info("We have finished multiplying the data")
            self.stop = True
            self.output_queue.put(None)
            return
        tag =  obj['tag']
        value = obj['value']
        new_value = value * self.gain
        logging.debug("Proportional actor received data (tag: %2.e, value: %2.e ), multiplied and sent out: (tag: %2.e, value: %2.e)" % (tag, value, tag, new_value ))
        data = {
            "tag": tag,
            "value": new_value
            }
        self.output_queue.put(data)
        obj = None
        
