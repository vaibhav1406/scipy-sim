
import logging
from numpy import sin, pi
#from Actor import Source, Actor
from scipysim.actors import Siso

class Sin(Siso):
    '''
    This actor is a generic sinusoid, it requires an input
    specifying the time steps. This allows arbitrarily dense time,
    or fixed width discrete time.
    '''

    def __init__(self, input_tags, out, amplitude=1.0, freq=0.1, phi=0.0):
        """
        default parameters create len(input_tags) samples of an F=0.1 sinusoid with an 
        amplitude of 1 and a phase of 0.
        """
        super(Sin, self).__init__(input_channel=input_tags, output_channel=out)

        self.amplitude = amplitude
        self.frequency = freq
        self.phase = phi

    def siso_process(self, obj):
        """The Sin trig function."""
        logging.debug("Running sin process")

        tag = obj['tag']
        value = self.amplitude * sin(2 * pi * self.frequency * tag + self.phase)

        data = {
                "tag": tag,
                "value": value
                }
        return data
