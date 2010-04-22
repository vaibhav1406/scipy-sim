'''
This Sum actor takes any number of input channels and adds up the data points
where the tags coincide, if there are missing tags it can discard the data point
or alternatively sum the remaining inputs.

@todo There is a bug where two unmatched channels. One channel finishes 
and a 'None' object gets treated like a dictionary... same in subtract.py

Created on 24/11/2009

@author: brian
'''
import logging
logging.basicConfig(level=logging.DEBUG)
import numpy as np
from scipysim.actors import Actor, Channel

class Summer(Actor):
    '''
    This actor takes a list of two or more sources and adds them
    together at the corresponding tagged time.
    This has to be used with discrete signals, or at least aligned continuous signals.
    '''
    num_outputs = 1
    num_inputs = None

    def __init__(self, inputs, output_channel, discard_incomplete_sets=True):
        """
        Constructor for a summation block

        @param inputs: A Python list of input channels for summing.

        @param output_channel: A single channel where the output will be put.

        @param discard_incomplete_sets: Boolean for either outputting incomplete
        data sets, or discarding.

        """
        super(Summer, self).__init__(output_channel=output_channel)
        self.inputs = list(inputs)
        self.num_inputs = len(self.inputs)
        self.discard_incomplete = discard_incomplete_sets
        self.data_is_stored = False
        self.future_data = []


    def process(self):
        """Wait for data from both (all) input channels"""
        logging.debug("Running summer process")

        # this is blocking on each channel in sequence
        objects = [in_channel.get(True) for in_channel in self.inputs]

        # We are finished iff all the input objects are None, but we still have to process the future data
        if objects.count(None) == len(objects):
            while len(self.future_data) > 0:
                oldest_tag = min([obj['tag'] for obj in self.future_data])
                current_data = [obj for obj in self.future_data if obj['tag'] == oldest_tag]
                if len(current_data) == len(self.inputs) or not self.discard_incomplete:
                    logging.debug("We are summing up what we have and outputting")
                    the_sum = sum([obj['value'] for obj in current_data])
                    self.output_channel.put(
                        {
                            'tag':oldest_tag,
                            'value': the_sum
                        }
                    )
                else:
                    logging.debug("We are throwing away the oldest tag, and storing the rest")
                [self.future_data.remove(item) for item in self.future_data if item['tag'] == oldest_tag]

            logging.info("We have finished summing the data")
            self.stop = True
            self.output_channel.put(None)
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
            self.output_channel.put(data)
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
            # EVERY input channel. So this would be sub optimal also...

            # need oldest tag out of stored and new
            oldest_tag = min(tags + [a['tag'] for a in self.future_data])

            if self.data_is_stored:
                logging.debug("We have got previously stored data - checking for any at oldest tag")
                current_data = [obj for obj in self.future_data + objects if obj['tag'] == oldest_tag]
            else:
                current_data = [obj for obj in objects if obj['tag'] == oldest_tag]


            # At this point we either sum ALL we have at 'now' or discard 'now'
            # depending on how many data points there are relative to inputs

            num_points = len(current_data)

            if num_points == len(self.inputs) or not self.discard_incomplete:
                logging.debug("We are summing up what we have and outputting")
                the_sum = values = sum([obj['value'] for obj in current_data])
                self.output_channel.put(
                    {
                        'tag':oldest_tag,
                        'value': the_sum
                    }
                )
            else:
                logging.debug("We are throwing away the oldest tag, and storing the rest")

            # Provided its not the very oldest data point (either saved already or arrived
            # in this process, we keep it for the future.
            self.future_data = [obj for obj in self.future_data + objects if obj['tag'] is not oldest_tag]
            if self.future_data is not None: self.data_is_stored = True

        # if the tags won't be the same -  we store a buffer of future tag/value pairs
        #future = max(tags)


import unittest

class SummerTests(unittest.TestCase):
    def test_basic_summer(self):
        '''Test adding two channels of complete pairs together'''
        q_in_1 = Channel()
        q_in_2 = Channel()
        q_out = Channel()

        input1 = [{'value':1, 'tag':i} for i in xrange(100)]
        input2 = [{'value':2, 'tag':i} for i in xrange(100)]

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
            self.assertEquals(q_out.get()['value'], 3)
        self.assertEquals(q_out.get(), None)

    def test_delayed_summer(self):
        '''
        Test adding two channels where one is delayed by ONE time step difference
        Summer is set up to discard incomplete sets
        '''
        q_in_1 = Channel()
        q_in_2 = Channel()
        q_out = Channel()

        input1 = [{'value':1, 'tag':i} for i in xrange(100)]
        input2 = [{'value':2, 'tag':i + 1} for i in xrange(100)]

        summer = Summer([q_in_1, q_in_2], q_out, True)
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

    def test_delayed_summer2(self):
        '''
        Test adding two channels where one is delayed by an arbitrary
        time step difference. Summer is set up to discard incomplete sets
        '''
        DELAY = 2
        q_in_1 = Channel()
        q_in_2 = Channel()
        q_out = Channel()

        input1 = [{'value':1, 'tag':i} for i in xrange(100)]
        input2 = [{'value':2, 'tag':i + DELAY} for i in xrange(100)]

        summer = Summer([q_in_1, q_in_2], q_out, True)
        summer.start()
        for val in input1:
            q_in_1.put(val)
        for val in input2:
            q_in_2.put(val)
        q_in_1.put(None)
        q_in_2.put(None)
        summer.join()
        #for i in xrange(DELAY, 99):

        self.assertEquals(q_out.get()['value'], 3)
        #self.assertEquals(q_out.get(), None)


    def test_delayed_summer3(self):
        '''
        Test adding two channels where one is delayed by ONE time step difference
        Summer is set up to SUM incomplete sets
        '''
        q_in_1 = Channel()
        q_in_2 = Channel()
        q_out = Channel()

        input1 = [{'value':1, 'tag':i} for i in xrange(100)]         # First tag is 0, last tag is 99.
        input2 = [{'value':2, 'tag':i + 1} for i in xrange(100)]     # First tag is 1, last tag is 100.

        summer = Summer([q_in_1, q_in_2], q_out, False)
        summer.start()
        for val in input1:
            q_in_1.put(val)
        for val in input2:
            q_in_2.put(val)
        q_in_1.put(None)
        q_in_2.put(None)
        summer.join()

        # First value should be 1, next 99 should be 3, last should be 2.
        data = q_out.get()
        self.assertEquals(data['value'], 1)
        self.assertEquals(data['tag'], 0)

        for i in xrange(1, 100):
            data = q_out.get()
            self.assertEquals(data['value'], 3)
            self.assertEquals(data['tag'], i)

        data = q_out.get()
        self.assertEquals(data['value'], 2)
        self.assertEquals(data['tag'], 100)
        # lastly the channel should contain a 'None'
        self.assertEquals(q_out.get(), None)

    def test_multi_summer(self):
        '''
        Test adding multiple (50) input signals
        where all signals contain every tag.
        '''
        num_input_channels, num_data_points = 50, 100

        input_channels = [Channel() for i in xrange(num_input_channels)]
        output_channel = Channel()

        # Fill each channel with num_data_points of its own index
        # So channel 5 will be full of the value 4, then a None
        for i, input_channel in enumerate(input_channels):
            _ = [input_channel.put({'value':i, 'tag':j}) for j in xrange(num_data_points)]
        _ = [input_channel.put(None) for input_channel in input_channels]

        summer = Summer(input_channels, output_channel)
        summer.start()
        summer.join()
        s = sum(xrange(num_input_channels))
        for i in xrange(num_data_points):
            self.assertEquals(output_channel.get()['value'], s)
        self.assertEquals(output_channel.get(), None)

    def test_multi_delayed_summer(self):
        '''
        Test adding multiple (50) input signals where one signal is delayed.

        '''
        DELAY = 20
        num_input_channels, num_data_points = 50, 100

        input_channels = [Channel() for i in xrange(num_input_channels)]
        output_channel = Channel()

        # Fill each channel with num_data_points of its own index
        # So channel 5 will be full of the value 4, then a None
        for i, input_channel in enumerate(input_channels):
            _ = [input_channel.put({'value':i, 'tag':j}) for j in xrange(num_data_points) if i is not 0]
        _ = [input_channels[0].put({'value':0, 'tag':j + DELAY}) for j in xrange(num_data_points)]
        _ = [input_channel.put(None) for input_channel in input_channels]

        summer = Summer(input_channels, output_channel)
        summer.start()
        summer.join()
        s = sum(xrange(num_input_channels))
        for i in xrange(num_data_points - DELAY):
            self.assertEquals(output_channel.get()['value'], s)
        self.assertEquals(output_channel.get(), None)


if __name__ == "__main__":
    #unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(SummerTests)
    unittest.TextTestRunner(verbosity=4).run(suite)

