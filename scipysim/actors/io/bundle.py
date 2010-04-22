
import logging
from scipysim.actors import Actor, Channel


import unittest
import numpy

class Bundle(Actor):
    '''
    This buffering/compressing/bundling actor takes a source 
    and waits for a preset number 
    of events (or for the signal to finish) before passing them on in one.
    
    They get passed on as a special condensed packet.
    '''

    num_inputs = 1
    num_outputs = 1

    def __init__(self, input_channel, output_channel, bundle_size=None):
        """
        Constructor for a bundle block.

        @param input_channel: The input channel to be bundled

        @param output_channel: The output channel that has been bundled

        @param bundle_size: The max size of an output bundle. Default
        is to buffer the whole signal then output a single bundle.
        """
        super(Bundle, self).__init__(input_channel=input_channel, output_channel=output_channel)
        self.bundle_size = bundle_size
        self.temp_data = []

    def process(self):
        """Send packets of events at one time"""
        logging.debug("Running buffer/bundle process")
        obj = self.input_channel.get(True)     # this is blocking
        if obj is not None:
            self.temp_data.append(obj)
        if obj is None or self.bundle_size is not None and len(self.temp_data) >= self.bundle_size:
            self.send_bundle()

            if obj is None:
                self.output_channel.put(None)
                self.stop = True
            else:
                self.temp_data = []

    def send_bundle(self):
        '''
        Create a numpy data type that can carry all the 
        information then add it to the output channel
        '''
        x = numpy.zeros(len(self.temp_data),
                            dtype=
                            {
                                'names': ["Tag", "Value"],
                                'formats': ['f8', 'f8'],
                                'titles': ['Domain', 'Name']    # This might not get used...
                             }
                        )
        x[:] = [ (element['tag'], element['value']) for element in self.temp_data if element is not None]
        self.output_channel.put(x)


