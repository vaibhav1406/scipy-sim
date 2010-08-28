'''
This Sum actor takes any number of input channels and adds up the data points
where the tags coincide, if there are missing tags it can discard the data point
or alternatively sum the remaining inputs.

@todo There is a bug where two unmatched channels. One channel finishes 
and a 'None' object gets treated like a dictionary... same in subtract.py

Created on 24/11/2009

@author: Brian Thorne
'''
import logging
#logging.basicConfig(level=logging.DEBUG)
from numpy import inf as infinity
from scipysim.actors import Actor, Channel, Event

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


    def process(self):
        '''
        Note that this only removes events from those channels that result
        in an output event. Events at the head of other channels are left
        untouched, and will be checked again the next time the process runs.
        '''

        logging.debug("Summer: running")

        # Block on each channel in sequence. We can't make a decision
        # on the sum until we have events (and thus tags) on every channel.
        events = []
        termination_count = 0
        oldest_tag = infinity
        for input in self.inputs:
            event = input.head()
            if event is None:
                termination_count += 1
            else:
                oldest_tag = min(oldest_tag, event.tag)
                events.append((input, event))


        # We are finished iff all the input channels have None at the head
        if termination_count == self.num_inputs:
            logging.info("Summer: finished summing all events")

            # Clear all input channels
            for input in self.inputs:
                input.drop()

            # Terminate this process and pass on termination signal
            self.stop = True
            self.output_channel.put(None)
            return

        elif termination_count > 0:
            # If we received at least one termination event then we should
            # begin to pass on termination signals

            # Clear non-terminating inputs
            for input in self.inputs:
                if input.head() is not None:
                    input.drop()

            # Terminate
            self.output_channel.put(None)

        else:
            # Otherwise there are still events to process.
            # We sum all the values at the oldest tag value. (0th option)
            # Alternatively (1) we could discard this time step if some tags don't match,
            # (2) We could do some sort of integration, histogram style sum for
            # continuous time systems. My (Brian's) feeling is that a CT sum is going
            # to have to be too different to be implemented in the same actor.
            sum = 0
            incomplete = False
            for input, event in events:
                if event.tag == oldest_tag:
                    sum += event.value

                    # Remove the head from each channel that has produced an output
                    input.drop()
                else:
                    incomplete = True

            if not (incomplete and self.discard_incomplete):
                self.output_channel.put(Event(oldest_tag, sum))


import unittest

class SummerTests(unittest.TestCase):
    def test_basic_summer(self):
        '''Test adding two channels of complete pairs together'''
        q_in_1 = Channel()
        q_in_2 = Channel()
        q_out = Channel()

        input1 = [Event(value=1, tag=i) for i in xrange(100)]
        input2 = [Event(value=2, tag=i) for i in xrange(100)]

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

        input1 = [Event(value=1, tag=i) for i in xrange(100)]
        input2 = [Event(value=2, tag=i+1) for i in xrange(100)]

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

        input1 = [Event(value=1, tag=i) for i in xrange(100)]
        input2 = [Event(value=2, tag=i + DELAY) for i in xrange(100)]

        summer = Summer([q_in_1, q_in_2], q_out, True)
        summer.start()
        for val in input1:
            q_in_1.put(val)
        for val in input2:
            q_in_2.put(val)
        q_in_1.put(None)
        q_in_2.put(None)
        summer.join()

        for i in xrange(DELAY, 100):
            self.assertEquals(q_out.get()['value'], 3)
        self.assertEquals(q_out.get(), None)


    def test_delayed_summer3(self):
        '''
        Test adding two channels where one is delayed by ONE time step difference
        Summer is set up to SUM incomplete sets
        '''
        q_in_1 = Channel()
        q_in_2 = Channel()
        q_out = Channel()

        input1 = [Event(value=1, tag=i) for i in xrange(100)]         # First tag is 0, last tag is 99.
        input2 = [Event(value=2, tag=i + 1) for i in xrange(100)]     # First tag is 1, last tag is 100.

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
            [input_channel.put(Event(value=i, tag=j)) for j in xrange(num_data_points)]
        [input_channel.put(None) for input_channel in input_channels]

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
            [input_channel.put(Event(value=i, tag=j)) for j in xrange(num_data_points) if i is not 0]
        [input_channels[0].put(Event(value=0, tag=j + DELAY)) for j in xrange(num_data_points)]
        [input_channel.put(None) for input_channel in input_channels]

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

