'''
Created on 23/11/2009

@author: Brian Thorne
'''

import logging
import numpy
from Actor import Actor

import Queue as queue

class Proportional(Actor):
    '''
    This actor takes a source and multiplies it by some gain P.
    '''

    def __init__(self, input, out, gain=2.0):
        """
        Constructor for a Proportional Actor.
        
        @param gain: the multiplicand - default is 2.0 to double the signal
        """
        Actor.__init__(self, input_queue=input, output_queue=out)

        self.gain = gain

    def process(self):
        """Multiply the input values by a gain..."""
        logging.debug("Running proportional process")

        obj = self.input_queue.get(True)     # this is blocking
        if obj is None:
            logging.info("We have finished multiplying the data")
            self.stop = True
            self.output_queue.put(None)
            return
        tag = obj['tag']
        value = obj['value']
        new_value = value * self.gain
        logging.debug("Proportional actor received data (tag: %2.e, value: %2.e ), multiplied and sent out: (tag: %2.e, value: %2.e)" % (tag, value, tag, new_value))
        data = {
            "tag": tag,
            "value": new_value
            }
        self.output_queue.put(data)
        obj = None

import unittest
class ProportionalTests(unittest.TestCase):
    '''Test the Proportional Actor'''
    def test_basic_proportional(self):
        '''Test doubling a queue.'''
        q_in = queue.Queue()
        q_out = queue.Queue()

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
