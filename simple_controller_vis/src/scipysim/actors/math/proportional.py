'''
Created on 23/11/2009

@author: Brian Thorne
'''

import logging
import numpy
from scipysim.actors import Siso, Channel

class Proportional(Siso):
    '''
    This actor takes a source and multiplies it by some gain P.
    '''

    def __init__(self, input, out, gain=2.0):
        """
        Constructor for a Proportional Actor.
        
        @param gain: the multiplicand - default is 2.0 to double the signal
        """
        super(Proportional, self).__init__(input_channel=input, output_channel=out)
        self.gain = gain

    def siso_process(self, obj):
        """Multiply the input values by a gain..."""
        logging.debug("Running proportional process")
        tag, value = obj['tag'], obj['value']

        new_value = value * self.gain if not value is None else value
        #logging.debug( "Proportional actor received data (tag: %2.e, value: %2.e ), multiplied and sent out: (tag: %2.e, value: %2.e)" % ( tag, value, tag, new_value ) )

        data = {
            "tag": tag,
            "value": new_value
            }
        return data

import unittest
class ProportionalTests(unittest.TestCase):
    '''Test the Proportional Actor'''
    def test_basic_proportional(self):
        '''Test doubling a channel.'''
        q_in = Channel()
        q_out = Channel()

        inp = [{'value':1, 'tag':i} for i in xrange(100)]
        expected_output = [{'value':2, 'tag':i} for i in xrange(100)]

        doubler = Proportional(q_in, q_out)
        doubler.start()
        [q_in.put(val) for val in inp]
        q_in.put(None)
        doubler.join()

        for i in xrange(100):
            out = q_out.get()
            self.assertEquals(out['value'], expected_output[i]['value'])
            self.assertEquals(out['tag'], expected_output[i]['tag'])
        self.assertEquals(q_out.get(), None)

if __name__ == "__main__":
    unittest.main()
