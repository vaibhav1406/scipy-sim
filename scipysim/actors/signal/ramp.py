'''
Created on 23/11/2009

@author: Brian Thorne
@author: Allan McInnes
'''
import logging
from numpy import linspace
from scipysim import Source, Actor, Event, LastEvent

import time, random # These are used to test the async

class Ramp(Source):
    '''
    A ramp source
    '''

    def __init__(self, out, amplitude=2.0, freq=1.0 / 30, resolution=10, simulation_time=120, endpoint=False):
        """
        Default parameters creates a ramp up to 2 that takes 30 seconds with 10 values per "second"

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

            self.output_channel.put(Event(tag, value))
            #logging.debug("Ramp process added data: (tag: %2.e, value: %.2e)" % (tag, value))
            #time.sleep(random.random() * 0.001)     # Adding a delay so we can see the async
        logging.debug("Ramp process finished adding all data to channel")
        self.stop = True
        self.output_channel.put(LastEvent(self.simulation_time))

