
import logging
import numpy
from Actor import Source, Actor

class Sin(Actor):
    '''
    This actor is a generic sinusoid, it requires an input
    specifying the time steps. This allows arbitrarily dense time,
    or fixed width discrete time.
    '''

    def __init__(self, input_tags, out, amplitude=1.0, freq=0.1, phi=0.0):
        """
        default parameters create len(input_tags) samples of an F=0.1 sinusoid with an 
        amplitude of 1 and a phase of 0.

        @param out: An output channel (with a specified type ???)
        """
        Actor.__init__(self, output_queue=out)
        #@todo Change the output queue assertion
        #assert out.domain is "DT"
        self.amplitude = amplitude
        self.frequency = freq
        self.phase = phi

    def process(self):
        """Create the numbers..."""
        logging.debug("Running DT sinusoid process")
        
        obj = self.input_queue.get(True)     # this is blocking
        if obj is None:
            logging.info('We have finished "sinning" the data')
            self.stop = True
            self.output_queue.put(None)
            return
        tag = obj['tag']
        
        value = self.amplitude * numpy.sin(2 * numpy.pi * self.frequency * tag + self.phase)

        data = {
                "tag": tag,
                "value": value
                }
        self.output_queue.put(data)
