'''
Created on 24/11/2009

@author: brian
'''
import logging
import numpy as np
from Actor import Actor

import Queue as queue

#import time, random # These are or can be used to test the async




class Summer(Actor):
    '''
    This actor takes a list of two or more sources and adds them
    together at the corresponding tagged time.
    This has to be used with discrete signals, or at least aligned continuous signals.
    '''

    def __init__(self, inputs, output_queue, discard_incomplete_sets=True):
        """
        Constructor for a summation block
        """
        Actor.__init__(self, output_queue=output_queue)
        self.inputs = list(inputs)
        self.discard_incomplete = discard_incomplete_sets
        self.data_is_stored = False
        #self.futures = np.zeros_like(self.inputs)


    def process(self):
        """Wait for data from both (all) input queues"""
        logging.debug("Running summer process")

        # this is blocking on each queue in sequence
        objects = [in_queue.get(True) for in_queue in self.inputs]

        # We are finished iff all the input objects are None
        if objects.count(None) == len(objects):
            logging.info("We have finished summing the data")
            self.stop = True
            self.output_queue.put(None)
            return
        tags = [obj['tag'] for obj in objects]
        values = [obj['value'] for obj in objects]

        if tags.count(tags[0]) == len(tags):
            # If all tags are the same we can sum the values and output
            new_value = sum(values)
            logging.debug("Summer received all equally tagged inputs, summed and sent out: (tag: %2.e, value: %2.e)" % (tags[0], new_value))
            data = {
                    "tag": tags[0],
                    "value": new_value
                    }
            self.output_queue.put(data)
        else:
            logging.debug("Tags were not all equal... First two tags: %.5e, %.5e" % (tags[0], tags[1]))
            # Since they are not equal, and the tags are always sequential, the oldest timed tags are NEVER
            # going to have equivalent values from the buffers that have returned newer tags.
            # So we sum all the values at the oldest tag value. (0th option)
            # Alternatively (1) we could discard this time step
            # (2) We could do some sort of integration, histogram style sum for continuous time systems
            # My feeling is that a CT sum is going to have to be to different to be implemented it the same actor.

            # With the 0th option there is a major problem when one signal isn't creating the same rate of signals
            # because the current actor (without director) model only processes after receiving an input from
            # EVERY input queue. So this would be sub optimal also...
            oldest_tag = min(tags)

            if self.data_is_stored:
                logging.debug("We have got previously stored data - checking for any at oldest tag")
                current_data = [obj for obj in self.future_data + objects if obj['tag'] == oldest_tag]


                logging.debug("We have data stored from the future for 'now'...")
                # At this point we either sum ALL we have at 'now' or discard 'now'
                # depending on how many data points there are relative to inputs

                num_points = len(current_data)


                if num_points == len(self.inputs) or not self.discard_incomplete:
                    the_sum = values = sum([obj['value'] for obj in current_data])
                    self.output_queue.put(
                        {
                            'tag':oldest_tag,
                            'value': the_sum
                        }
                    )
                else:
                    logging.debug("We are throwing away the oldest tag, and storing the rest")

            self.future_data = [obj for obj in objects if obj['tag'] is not oldest_tag]
            if self.future_data is not None: self.data_is_stored = True

        # if the tags won't be the same -  we store a buffer of future tag/value pairs
        #future = max(tags)


import unittest

class SummerTests(unittest.TestCase):
    def test_basic_summer(self):
        '''Test adding two queues of complete pairs together'''
        q_in_1 = queue.Queue()
        q_in_2 = queue.Queue()
        q_out = queue.Queue()

        input1 = [{'value':1,'tag':i} for i in xrange(100)]
        input2 = [{'value':2,'tag':i} for i in xrange(100)]

        summer = Summer([q_in_1, q_in_2], q_out)
        summer.start()
        for val in input1:
            q_in_1.put(val)
        for val in input2:
            q_in_2.put(val)
        q_in_1.put(None)
        q_in_2.put(None)
        summer.join()
        for i in xrange(100):
            self.assertEquals(q_out.get()['value'],3)
        self.assertEquals(q_out.get(), None)

    def test_delayed_summer(self):
        '''Test adding two queues where one is delayed by some amount'''
        q_in_1 = queue.Queue()
        q_in_2 = queue.Queue()
        q_out = queue.Queue()

        input1 = [{'value':1,'tag':i} for i in xrange(100)]
        input2 = [{'value':2,'tag':i + 1} for i in xrange(100)]

        summer = Summer([q_in_1, q_in_2], q_out)
        summer.start()
        for val in input1:
            q_in_1.put(val)
        for val in input2:
            q_in_2.put(val)
        q_in_1.put(None)
        q_in_2.put(None)
        summer.join()
        for i in xrange(99):
            self.assertEquals(q_out.get()['value'], 3)
        self.assertEquals(q_out.get(), None)

    def test_multi_summer(self):
        '''
        Test adding multiple (50) input signals
        where all signals contain every tag.
        '''
        num_input_queues, num_data_points = 50, 100

        input_queues = [queue.Queue() for i in xrange(num_input_queues)]
        output_queue = queue.Queue()

        # Fill each queue with num_data_points of its own index
        # So queue 5 will be full of the value 4, then a None
        for i, input_queue in enumerate(input_queues):
            _ = [input_queue.put({'value':i,'tag':j}) for j in xrange(num_data_points)]
        _ = [input_queue.put(None) for input_queue in input_queues]

        summer = Summer(input_queues, output_queue)
        summer.start()
        summer.join()
        s = sum(xrange(num_input_queues))
        for i in xrange(num_data_points):
            self.assertEquals(output_queue.get()['value'], s)
        self.assertEquals(output_queue.get(), None)
if __name__ == "__main__":
    unittest.main()
