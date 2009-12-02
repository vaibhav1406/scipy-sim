'''
Created on 03/12/2009

@author: allan
'''
import logging
import numpy
from Actor import Source, Actor

class CTSin(Source):
    '''
    This actor is a continuous-time sinusoid source.
    Frequency is specified in Hz, and phase in radians.
    '''

    def __init__(self, out, amplitude=1.0, freq=1.0, phi=0.0, timestep=0.001, simulation_time=10):
        """
        default parameters create a 1 Hz sinusoid with an amplitude of 1 and a phase of 0.

        """
        Actor.__init__(self, output_queue=out)
        self.amplitude = amplitude
        self.frequency = freq
        self.phase = phi
        self.dt = timestep
        self.simulation_time = simulation_time

    def process(self):
        """Create the numbers..."""
        logging.debug("Running CT sinusoid process")
        tags = numpy.linspace(0, self.simulation_time, self.simulation_time/self.dt) 

        for tag in tags:
            value = self.amplitude * numpy.sin(2 * numpy.pi * self.frequency * tag + self.phase)

            data = {
                    "tag": tag,
                    "value": value
                    }
            self.output_queue.put(data)
        logging.debug("CT Sinusoid process finished adding all data to queue")
        self.stop = True
        self.output_queue.put(None)
