'''
Created on 19/11/2009
TODO
@author: brian
'''
from Actor import Source, Actor
import logging
import numpy
import time
import random

class RandomSource(Source):
    '''
    This signal source is just a random noise.
    '''


    def __init__(self, out, amplitude=1.0, res=10, simulation_time=120):
        '''
        Constructor for a RandomSource.

        @param out: The output queue to put the signal in.

        Optional Paramaters:

        @param amplitude: The amplitude of the noise

        @param res: the number of values to output "per second"
                    res defaults to 10

        @param simulation_time: The preset time that this will run for.
        '''
        Actor.__init__(self, output_queue=out)
        self.amplitude = amplitude
        self.resolution = res
        self.simulation_time = simulation_time

    def process(self):
        """Create the numbers..."""
        logging.debug("Running ramp process")
        tags = numpy.linspace(0, self.simulation_time, self.simulation_time*self.resolution)

        for tag in tags:
            value = random.random() * self.amplitude

            data = {
                    "tag": tag,
                    "value": value
                    }
            self.output_queue.put(data)
            logging.debug("Random process added data: (tag: %2.e, value: %.2e)" % (tag, value))
            #time.sleep(random.random() * 0.01)     # Adding a delay so we can see the async
        logging.debug("Random process finished adding all data to queue")
        self.stop = True
        self.output_queue.put(None)
