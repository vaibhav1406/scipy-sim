'''
Created on 23/11/2009

@author: brian
'''
import logging
from numpy import linspace
from scipysim.actors import Source, Actor

import time, random # These are used to test the async

class Ramp(Source):
    '''
    This actor is a ramp source
    '''

    def __init__(self, out, amplitude=2.0, freq=1.0 / 30, resolution=10, simulation_time=120, endpoint=False):
        """
        default parameters creates a ramp up to 2 that takes 30 seconds with 10 values per "second"

        """
        super(Ramp, self).__init__(output_channel=out, simulation_time=simulation_time)
        self.amplitude = amplitude
        self.frequency = freq
        self.resolution = resolution
        self.endpoint = endpoint


    def process(self):
        """Create the numbers..."""
        logging.debug("Running ramp process")
        tags = linspace(0, self.simulation_time, self.simulation_time * self.resolution, endpoint=self.endpoint)

        for tag in tags:
            value = tag * self.frequency * self.amplitude

            while value >= self.amplitude:
                value = value - self.amplitude

            data = {
                    "tag": tag,
                    "value": value
                    }
            self.output_channel.put(data)
            #logging.debug("Ramp process added data: (tag: %2.e, value: %.2e)" % (tag, value))
            #time.sleep(random.random() * 0.001)     # Adding a delay so we can see the async
        logging.debug("Ramp process finished adding all data to channel")
        self.stop = True
        self.output_channel.put(None)
