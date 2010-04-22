'''
Created on 19/11/2009
TODO
@author: brian
'''
from scipysim.actors import Source
import logging
from numpy import linspace
import time
import random

class RandomSource(Source):
    '''
    This signal source is just a random noise.
    '''


    def __init__(self, out, amplitude=1.0, resolution=10, simulation_time=120, endpoint=False):
        '''
        Constructor for a RandomSource.

        @param out: The output channel to put the signal in.

        Optional Paramaters:

        @param amplitude: The amplitude of the noise

        @param resolution: the number of values to output "per second",
        defaults to 10.

        @param simulation_time: The preset time to generate random numbers over,
        defaults to 120 seconds.
        
        @param endpoint: Whether to include the final point (120th second) 
        in the simulation.
        '''
        super(RandomSource, self).__init__(output_channel=out, simulation_time=simulation_time)
        self.amplitude = amplitude
        self.resolution = resolution
        self.endpoint = endpoint

    def process(self):
        """Create the numbers..."""
        logging.debug("Running ramp process")
        tags = linspace(0, self.simulation_time, self.simulation_time * self.resolution, endpoint=self.endpoint)

        for tag in tags:
            value = random.random() * self.amplitude

            data = {
                    "tag": tag,
                    "value": value
                    }
            self.output_channel.put(data)
            logging.debug("Random process added data: (tag: %2.e, value: %.2e)" % (tag, value))
            #time.sleep(random.random() * 0.01)     # Adding a delay so we can see the async
        logging.debug("Random process finished adding all data to channel")
        self.stop = True
        self.output_channel.put(None)
