'''
This actor makes an "IF" like structure.
The first input is a boolean tagged signal, at the tags where it is true
the other channel's data gets passed on, otherwise discarded.

Created on 13/12/2009

@author: Brian
'''
import logging
logging.basicConfig(level=logging.DEBUG)

import numpy as np
from Actor import Actor, Channel



class PassThrough(Actor):
    '''
    This actor takes a boolean tagged signal and a data channel.
    At the tag points where the boolean signal is True, the values from the input are
    passed on to the output. 

    @note: For now this has to be used with discrete signals, or at least aligned continuous signals.
    '''

    def __init__(self, bool_input, data_input, output_queue):
        """
        Constructor for a PassThrough block

        @param bool_input: A boolean tagged signal.
        
        @param data_input: The data to be passed through.

        @param output_queue: A single queue where the output will be put.
        """
        super(PassThrough, self).__init__(output_queue=output_queue)
        self.bool_input = bool_input
        self.data_input = data_input
        logging.info("We have set up a pass through actor")

    def process(self):
        """Wait for data from both input queues"""
        logging.debug("Running pass-through (IF) process, blocking on both queues")

        # this is blocking on each queue in sequence
        bool_in = self.bool_input.get(True)
        logging.debug("Got a boolean value, waiting for data point")
        data_in = self.data_input.get(True)
        logging.debug("Received a boolean and a data point.")

        # We are finished iff all the input objects are None
        if bool_in is None and data_in is None:
            logging.info("We have finished PassingThrough the data")
            self.stop = True
            self.output_queue.put(None)
            return
        
        # For now we require the signals are in sync
        assert bool_in['tag'] == data_in['tag']

        if bool_in['value'] is True:
            logging.debug("The input was positive, passing data through")
            self.output_queue.put(data_in)
        else:
            logging.debug("Discarding data.")
import unittest

class PassThroughTests(unittest.TestCase):
    def setUp(self):
        self.data_in = Channel()
        self.bool_in = Channel()
        self.output = Channel()
        
        # Some fake boolean data
        self.every_point = [True] * 100
        self.every_second_point = [True, False] * 50
        self.no_points = [False] * 100
        
        # some fake pass through data, and add it to the queue
        self.data = range(100)
        [self.data_in.put({'tag':i, 'value':i}) for i in range(100)]
        self.data_in.put(None)
        
        # create the block
        self.block = PassThrough(self.bool_in, self.data_in, self.output)
        
    def test_all_points(self):
        
        [self.bool_in.put({'tag':i, 'value':self.every_point[i]}) for i in self.data]
        self.bool_in.put(None)
        self.block.start()
        self.block.join()
        [self.assertEquals(self.output.get()['tag'], i) for i in self.data]
        self.assertEquals(None, self.output.get())
    
    def test_every_second_point(self):
        [self.bool_in.put({'tag':i, 'value':self.every_second_point[i]}) for i in self.data]
        self.bool_in.put(None)
        self.block.start()
        self.block.join()
        [self.assertEquals(self.output.get()['tag'], i) for i in self.data if i % 2 == 0]
        self.assertEquals(None, self.output.get())
        
    def test_no_points(self):
        [self.bool_in.put({'tag':i, 'value':self.no_points[i]}) for i in self.data]
        self.bool_in.put(None)
        self.block.start()
        self.block.join()
        self.assertEquals(None, self.output.get())

if __name__ == "__main__":
    unittest.main()
    #suite = unittest.TestLoader().loadTestsFromTestCase(PassThroughTests)
    #unittest.TextTestRunner(verbosity=4).run(suite)

