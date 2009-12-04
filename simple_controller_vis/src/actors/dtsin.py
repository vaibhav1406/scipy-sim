'''
Created on 04/12/2009

@author: allan
'''
import logging
import numpy
from Actor import Source, Actor

class DTSin(Source):
    '''
    This actor is a discrete-time sinusoid source.
    Frequency is specified in cycles/sample ("digital frequency" or 
    "normalized frequency"), and phase in radians.
    The domain of the signal is the integers.
    '''

    def __init__(self, out, amplitude=1.0, freq=0.1, phi=0.0, simulation_length=100):
        """
        default parameters create 50 samples of an F=0.1 sinusoid with an 
        amplitude of 1 and a phase of 0.

        """
        Actor.__init__(self, output_queue=out)
        self.amplitude = amplitude
        self.frequency = freq
        self.phase = phi
        self.simulation_length = simulation_length

    def process(self):
        """Create the numbers..."""
        logging.debug("Running DT sinusoid process")
        tags = numpy.arange(0, self.simulation_length, 1) 

        for tag in tags:
            value = self.amplitude * numpy.sin(2 * numpy.pi * self.frequency * tag + self.phase)

            data = {
                    "tag": tag,
                    "value": value
                    }
            self.output_queue.put(data)
        logging.debug("DT Sinusoid process finished adding all data to queue")
        self.stop = True
        self.output_queue.put(None)
