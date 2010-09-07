'''
Summer actors takes any number of input channels and adds the signals on each
channel to produce a single output signal. The semantics of the addition
depend on the kind of signals that are being added.

@author: Allan McInnes
@author: Brian Thorne
'''
import logging
#logging.basicConfig(level=logging.DEBUG)
from numpy import inf as infinity
from scipysim.actors import Actor, Channel, Event

class BaseSummer(Actor):
    '''
    Provides the core behaviour of a summation block.
    '''
    num_outputs = 1
    num_inputs = None

    def __init__(self, inputs, output_channel):
        """
        Constructor for a general summation block

        @param inputs: A Python list of input channels for summing. Elements
        of the list may optionally be tuples containing a string defining
        the sign of the input (e.g. [(in1, '+'), (in2, '-'), in3] ). If the
        sign is not specified then it defaults to '+'.

        @param output_channel: A single channel where the output will be put.

        """
        super(BaseSummer, self).__init__(output_channel=output_channel)

        domain = output_channel.domain
        for input in inputs:
            # Unpack input tuples
            inp = input[0] if isinstance(input, tuple) else input

            if not inp.domain == domain:
                raise TypeError, "Summer channels must all have the same domain."

        self.signs = {}
        self.inputs = []
        for input in list(inputs):
            # Grab input channels
            self.inputs.append( input[0] if isinstance(input, tuple) else input )

            # Record signs for input channels. Default is +. The sign
            # string are converted to numbers.
            if isinstance(input, tuple):
                self.signs[input[0]] = float(input[1]+'1.0')
            else:
                self.signs[input] = 1.0

        self.num_inputs = len(self.inputs)

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
        oldest_tag = infinity
        for input in self.inputs:
            event = input.head()
            if event is not None:
                oldest_tag = min(oldest_tag, event.tag)
                events.append((input, event))


        # We are finished iff all the input channels have None at the head
        if len(events) < self.num_inputs:
            # If we received at least one termination event then we should
            # begin to pass on termination signals

            # Clear non-terminating inputs
            for input in self.inputs:
                if input.head() is not None:
                    input.drop()

            # Send termination signal
            self.output_channel.put(None)

            if len(events) == 0:
                # Terminate this process
                logging.info("Summer: finished summing all events")
                self.stop = True
                return
        else:
            # We sum all the values at the oldest tag value.
            sum, discard = self.sum(oldest_tag, events)
            if not discard:
                self.output_channel.put(Event(oldest_tag, sum))

    def sum(self, oldest_tag, events):
        '''This method must be overridden. It implements summation for
        a particular domain. Retursn discard = true if the output should
        be ignored
        @return sum, discard
        '''
        raise NotImplementedError


class DTSummer(BaseSummer):
    '''
    Takes a list of two or more input signals, and sums the values
    at the corresponding tags.

    This has to be used with discrete-time signals.
    '''

    def __init__(self, inputs, output_channel, discard_incomplete_sets=True):
        """
        Constructor for a discrete-time summation block

        @param inputs: A Python list of input channels for summing. Elements
        of the list may optionally be tuples containing a string defining
        the sign of the input (e.g. [(in1, '+'), (in2, '-'), in3] ). If the
        sign is not specified then it defaults to '+'.

        @param output_channel: A single channel where the output will be put.

        @param discard_incomplete_sets: Boolean for either outputting incomplete
        data sets, or discarding.

        """
        super(DTSummer, self).__init__(inputs = inputs, output_channel=output_channel)
        self.discard_incomplete = discard_incomplete_sets


    def sum(self, oldest_tag, events):
        """Sum all events at the oldest tag value, and ignore all others."""
        sum = 0
        incomplete = False
        for input, event in events:
            if event.tag == oldest_tag:
                sum += self.signs[input] * event.value

                # Remove the head from each channel that has produced an output
                input.drop()
            else:
                incomplete = True

        return (sum, (incomplete and self.discard_incomplete))


class CTSummer(BaseSummer):
    '''
    Takes a list of two or more input signals, and sums the values.
    Input events with matching tags have their values directly summed.
    A zero-order hold (constant interpolation) is assumed for signals that
    don't have a matching tag for the current processing step.
    '''

    def __init__(self, inputs, output_channel):
        """
        Constructor for a continuous-time summation block

        @param inputs: A Python list of input channels for summing. Elements
        of the list may optionally be tuples containing a string defining
        the sign of the input (e.g. [(in1, '+'), (in2, '-'), in3] ). If the
        sign is not specified then it defaults to '+'.

        @param output_channel: A single channel where the output will be put.

        """
        super(CTSummer, self).__init__(inputs = inputs, output_channel=output_channel)

        self.held_values= {}
        for input in self.inputs:
            # Initialize state
            self.held_values[input] = 0.0


    def sum(self, oldest_tag, events):
        """Sum all the values at the oldest tag value, and assume
        other signals maintain their previous value."""
        sum = 0
        for input, event in events:
            # Remove the head from each channel that has a matching tag,
            # and update the stored value
            if event.tag == oldest_tag:
                input.drop()
                self.held_values[input] = event.value

            sum += self.signs[input] * self.held_values[input]

        return (sum, False)

class Summer:
    '''
    Wrapper for summation blocks.
    '''
    num_inputs = None
    num_outputs = 1
    output_domains = (None,)
    input_domains = (None,)
    
    def __init__(self, inputs, output_channel):
        """
        Wrapper for summation blocks.

        @param inputs: A Python list of input channels for summing. Elements
        of the list may optionally be tuples containing a string defining
        the sign of the input (e.g. [(in1, '+'), (in2, '-'), in3] ). If the
        sign is not specified then it defaults to '+'.

        @param output_channel: A single channel where the output will be put.

        """
        domain = output_channel.domain
        if domain == 'CT':
            self.__summer = CTSummer(inputs, output_channel)
        elif domain == 'DT':
            self.__summer = DTSummer(inputs, output_channel)
        else:
            raise NotImplementedError, "No summer for " + domain + " domain."

    def __getattr__(self, arg):
        return getattr(self.__summer, arg)


import unittest

class SummerTests(unittest.TestCase):
    def test_basic_summer(self):
        '''Test adding two channels of complete pairs together'''
        q_in_1 = Channel('DT')
        q_in_2 = Channel('DT')
        q_out = Channel('DT')

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

    def test_input_domain_check(self):
        def run():
            q_in_1 = Channel('DT')
            q_in_2 = Channel('CT')
            q_out = Channel('DT')
            Summer([q_in_1, q_in_2], q_out)
        self.assertRaises(TypeError, run)

    def test_input_output_domain_check(self):
        def run():
            q_in_1 = Channel('DT')
            q_in_2 = Channel('DT')
            q_out = Channel('CT')
            Summer([q_in_1, q_in_2], q_out)
        self.assertRaises(TypeError, run)

    def test_signed_summer(self):
        '''Test subtracting one channel from another'''
        q_in_1 = Channel('DT')
        q_in_2 = Channel('DT')
        q_out = Channel('DT')

        input1 = [Event(value=1, tag=i) for i in xrange(100)]
        input2 = [Event(value=2, tag=i) for i in xrange(100)]

        summer = Summer([q_in_1, (q_in_2, '-')], q_out)
        summer.start()
        for val in input1:
            q_in_1.put(val)
        for val in input2:
            q_in_2.put(val)
        q_in_1.put(None)
        q_in_2.put(None)
        summer.join()
        for i in xrange(100):
            self.assertEquals(q_out.get()['value'], -1)
        self.assertEquals(q_out.get(), None)

    def test_delayed_summer(self):
        '''
        Test adding two channels where one is delayed by ONE time step difference
        Summer is set up to discard incomplete sets
        '''
        q_in_1 = Channel('DT')
        q_in_2 = Channel('DT')
        q_out = Channel('DT')

        input1 = [Event(value=1, tag=i) for i in xrange(100)]
        input2 = [Event(value=2, tag=i+1) for i in xrange(100)]

        summer = DTSummer([q_in_1, q_in_2], q_out, True)
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
        q_in_1 = Channel('DT')
        q_in_2 = Channel('DT')
        q_out = Channel('DT')

        input1 = [Event(value=1, tag=i) for i in xrange(100)]
        input2 = [Event(value=2, tag=i + DELAY) for i in xrange(100)]

        summer = DTSummer([q_in_1, q_in_2], q_out, True)
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
        q_in_1 = Channel('DT')
        q_in_2 = Channel('DT')
        q_out = Channel('DT')

        input1 = [Event(value=1, tag=i) for i in xrange(100)]         # First tag is 0, last tag is 99.
        input2 = [Event(value=2, tag=i + 1) for i in xrange(100)]     # First tag is 1, last tag is 100.

        summer = DTSummer([q_in_1, q_in_2], q_out, False)
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

    def test_ct_summer_with_different_rates(self):
        '''
        Test adding two channels where one is operates at a different
        rate than the other. The sum should appear at the fastest
        rate, with values that assume constant-interpolation between
        events in the slower channel.
        '''
        DELAY = 2
        q_in_1 = Channel('CT')
        q_in_2 = Channel('CT')
        q_out = Channel('CT')

        input1 = [Event(value=i, tag=i) for i in xrange(1,100)]
        input2 = [Event(value=2*i, tag=2*i) for i in xrange(1,50)]

        summer = Summer([q_in_1, q_in_2], q_out)
        summer.start()
        for val in input1:
            q_in_1.put(val)
        for val in input2:
            q_in_2.put(val)
        q_in_1.put(None)
        q_in_2.put(None)
        summer.join()

        self.assertEquals(q_out.get()['value'], 1.0)
        for i in xrange(2, 98, 2):
            self.assertEquals(q_out.get()['value'], i + i)
            self.assertEquals(q_out.get()['value'], i + i + 1)
        self.assertEquals(q_out.get()['value'], 196)
        self.assertEquals(q_out.get(), None)

    def test_multi_summer(self):
        '''
        Test adding multiple (50) input signals
        where all signals contain every tag.
        '''
        num_input_channels, num_data_points = 50, 100

        input_channels = [Channel('DT') for i in xrange(num_input_channels)]
        output_channel = Channel('DT')

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

        input_channels = [Channel('DT') for i in xrange(num_input_channels)]
        output_channel = Channel('DT')

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

