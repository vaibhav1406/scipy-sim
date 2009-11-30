'''
Created on 23/11/2009

@author: Brian Thorne
'''

import logging
import numpy
from Actor import Source, Actor

try:
    import queue
except ImportError:
    import Queue as queue

import time, random # These are used to test the async

class Delay(Actor):
    '''
    This actor takes a source and delays it by an arbitrary amount of time.
    '''

    def __init__(self, input, out, wait=1.0/10):
        """
        Constructor for a delay block.

        @param input: The input queue to be delayed

        @param out: The output queue that has been delayed

        @param wait: The delay time in seconds. Defaults to delaying
                     the signal by one tenth of a second.
        """
        super(Delay, self).__init__(input_queue=input, output_queue=out)
        self.delay = wait

    def process(self):
        """Delay the input values by a set amount of time..."""
        logging.debug("Running delay process")

        obj = self.input_queue.get(True)     # this is blocking
        if obj is None:
            logging.info("We have finished delaying the data")
            self.stop = True
            self.output_queue.put(None)
            return
        tag =  obj['tag'] + self.delay
        value = obj['value']
        data = {
            "tag": tag,
            "value": value
            }
        self.output_queue.put(data)
        obj = None

import unittest

class DelayTests(unittest.TestCase):
    def test_basic_delay(self):
        delay = 1
        q_in = queue.Queue()
        q_out = queue.Queue()

        input1 = [{'value': 1, 'tag': i } for i in xrange(100)]
        expected_output = [{'value':1,'tag': i+1 } for i in xrange(100)]

        block = Delay(q_in, q_out, delay)
        block.start()
        [q_in.put(i) for i in input1 + [None]]

        block.join()
        actual_output = [q_out.get() for i in xrange(100)]
        [self.assertEquals( actual_output[i], expected_output[i]) for i in xrange(100)]
        self.assertEquals(None, q_out.get())

if __name__ == "__main__":
    unittest.main()
