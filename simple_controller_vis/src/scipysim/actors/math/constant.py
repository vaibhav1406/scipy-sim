'''
Created on 23/11/2009

@author: brian
'''
import logging
from numpy import linspace
from scipysim.actors import Source

class Constant(Source):
    '''
    This actor is a constant value source
    '''

    def __init__(self, out, value=1.0, resolution=10, simulation_time=120, endpoint=False):
        """
        default parameters creates a constant output of 1.0 for 2 minutes (with 10 values per "second")

        """
        super(Constant, self).__init__(output_channel=out, simulation_time=simulation_time)
        self.resolution = resolution
        self.endpoint = endpoint
        self.value = value


    def process(self):
        """Create the numbers..."""
        logging.debug("Running ramp process")
        tags = linspace(0, self.simulation_time, self.simulation_time * self.resolution, endpoint=self.endpoint)  # for now just compute 2 minutes of values

        [self.output_channel.put({
                    "tag": tag,
                    "value": self.value
                }) for tag in tags]

        #time.sleep(random.random() * 0.001)     # Adding a delay so we can see the async
        logging.debug("Const process finished adding all data to its output channel")
        self.stop = True
        self.output_channel.put(None)
