'''
Created on 24/11/2009

@author: brian
'''
import logging
import numpy as np
from Actor import Actor
from multiqueue import MultiQueue
import Queue as queue

MAX_INPUTS = 10


class Summer(Actor):
    '''
    This actor sums the input at each tagged time and outputs the result.
    
    This has to be used with discrete signals, 
    or at least aligned continuous signals (floating tags will break it)
    '''

    def __init__(self, input_queue, output_queue):
        """
        Constructor for a summation block
        
        @param input_queue
        a single queue that is connected to one or more sources and adds
        them together at the times where the tags correspond.
        
        @param output_queue
        The queue to put the resulting sum on.
        """
        Actor.__init__(self, input_queue=input, output_queue=output_queue)
        self.future_values = []



    def process(self):
        """Wait for data from both (all) input queues"""
        logging.debug("Running summer process")

        # this is blocking on the queue
        object = self.input_queue.get(True)

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
            logging.debug("Summer received all equally tagged inputs, summed and sent out: (tag: %2.e, value: %2.e)" % (tags[0], new_value))
            data = {
                    "tag": tags[0],
                    "value": new_value
                    }
            self.output_queue.put(data)
        else:
            logging.debug("Tags were not all equal... First two tags: %.5e, %.5e" % (tags[0], tags[1]))
            # Since they are not equal, and the tags are always sequential, the oldest timed tags are NEVER
            # going to have equivalent values from the buffers that have returned newer tags.
            # So we sum all the values at the oldest tag value. (0th option)
            # Alternatively (1) we could discard this time step
            # (2) We could do some sort of integration, histogram style sum for continuous time systems
            # My feeling is that a CT sum is going to have to be to different to be implemented it the same actor.

            # With the 0th option there is a major problem when one signal isn't creating the same rate of signals
            # because the current actor (without director) model only processes after receiving an input from
            # EVERY input queue. So this would be sub optimal also... 

        # if the tags won't be the same -  we store a buffer of future tag/value pairs
        #future = max(tags)
