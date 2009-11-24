'''
Created on 24/11/2009

@author: brian
'''
import logging
import numpy
from Actor import Source, Actor

try:
    import queue
except ImportError:
    import Queue as queue
    
import time, random # These are used to test the async

class Summer(Actor):
    '''
    This actor takes two sources (for now) and adds them together at the corresponding tagged time. 
    This has to be used with discrete signals, or at least aligned continuous signals.
    '''
    
    def __init__(self, inputs, output_queue):
        """
        Constructor for a summation block
        """
        Actor.__init__(self, output_queue=output_queue)
        self.inputs = list(inputs)
        self.futures = numpy.zeros_like(self.inputs)
        
        
    def process(self):
        """Wait for data from both (all) input queues"""
        logging.debug("Running summer process")
        
        objects = [in_queue.get(True) for in_queue in self.inputs]     # this is blocking on each queue in sequence
                   
        # We are finished iff all the input objects are None
        if objects.count(None) == len(objects):
            logging.info("We have finished summing the data")
            self.stop = True
            self.output_queue.put(None)
            return
        tags = [obj['tag'] for obj in objects]
        values = [obj['value'] for obj in objects]
        
        if tags.count(tags[0]) == len(tags):
            # If all tags are the same we can sum the values and output
            new_value = sum(values)
            logging.debug("Summer had all the same tagged inputs, summed and sent out: (tag: %2.e, value: %2.e)" % (tags[0], new_value ))
            data = {
                    "tag": tags[0],
                    "value": new_value
                    }
            self.output_queue.put(data)
        
        # if the tags won't be the same -  we store a buffer of future tag/value pairs
        #future = max(tags)
        