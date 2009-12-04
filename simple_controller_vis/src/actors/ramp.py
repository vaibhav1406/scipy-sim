'''
Created on 23/11/2009

@author: brian
'''
import logging
import numpy
from Actor import Source, Actor

import time, random # These are used to test the async

class Ramp(Source):
    '''
    This actor is a ramp source
    '''

    def __init__(self, out, amplitude=2.0, freq=1.0/30, res=10, simulation_time=10):
        """
        default parameters creates a ramp up to 2 that takes 30 seconds with 10 values per "second"

        """
        Actor.__init__(self, output_queue=out)
        self.amplitude = amplitude
        self.frequency = freq
        self.resolution = res
        self.simulation_time = simulation_time

    def process(self):
        """Create the numbers..."""
        logging.debug("Running ramp process")
        tags = numpy.linspace(0, self.simulation_time, self.simulation_time*self.resolution)  # for now just compute 2 minutes of values

        for tag in tags:
            value = tag * self.frequency * self.amplitude

            while value >= self.amplitude:
                value = value - self.amplitude

            data = {
                    "tag": tag,
                    "value": value
                    }
            self.output_queue.put(data)
            #logging.debug("Ramp process added data: (tag: %2.e, value: %.2e)" % (tag, value))
            #time.sleep(random.random() * 0.001)     # Adding a delay so we can see the async
        logging.debug("Ramp process finished adding all data to queue")
        self.stop = True
        self.output_queue.put(None)
