'''
The merge actor takes any number of input channels and merges the signals. The 
resulting output signal maintains time ordering of tags. Events with identical
tags are placed in the output channel in an order that corresponds to the
ordering of the input channels from which the events are received. This makes
the merge deterministic.

@author: Allan McInnes
'''

import logging
logging.basicConfig(level=logging.DEBUG)
from scipysim.actors import Actor, Channel, MakeChans, Event
from numpy import inf as infinity

class Merge(Actor):
    '''
    Take a list of two or more input channels, and merge the signals into
    a single output signal.
    '''
    num_outputs = 1
    num_inputs = None

    def __init__(self, inputs, output_channel):
        """
        Construct a merge block

        @param inputs: a list of input channels to be merged.

        @param output_channel: a single output channel.

        """
        super(Merge, self).__init__(output_channel=output_channel)
        self.inputs = list(inputs)
        self.num_inputs = len(self.inputs)


    def process(self):
        """Deterministically merge inputs from a set of channels.
        
        Note that this only removes events from those channels that result
        in an output event. Events at the head of other channels are left 
        untouched, and will be checked again the next time the process runs."""
        #logging.debug("Merge: running")

        # Block on each channel in sequence. We can't make a decision
        # on the merge until we have events (and thus tags) on every channel.
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
            logging.info("Merge: finished merging all events")

            # Clear all input channels
            for input in self.inputs:
                input.drop()

            # Terminate this process and pass on termination signal
            self.stop = True
            self.output_channel.put(None)
            return

        # Otherwise there are still events to process. Send out those events
        # corresponding to the oldest tag.
        for input, event in events:
            if event.tag == oldest_tag:
                self.output_channel.put(event)

                # Remove the head from each channel that has produced an output
                input.drop()




import unittest

class MergeTests(unittest.TestCase):
    def test_simple_merge(self):
        '''Test merging two channels of complete pairs together'''
        q_in_1 = Channel()
        q_in_2 = Channel()
        q_out = Channel()

        input1 = [Event(value=1, tag=i) for i in xrange(100)] + [None]
        input2 = [Event(value=2, tag=i) for i in xrange(100)] + [None]

        merge = Merge([q_in_1, q_in_2], q_out)
        merge.start()
        for val in input1:
            q_in_1.put(val)
        for val in input2:
            q_in_2.put(val)
        merge.join()
        for i in xrange(100):
            self.assertEquals(q_out.get().value, 1)
            self.assertEquals(q_out.get().value, 2)
        self.assertEquals(q_out.get(), None)

    def test_alternating_merge(self):
        '''
        Test merging two channels with out-of-sync tags.
        '''
        q_in_1 = Channel()
        q_in_2 = Channel()
        q_out = Channel()

        input1 = [Event(value=1, tag=2.0*i) for i in xrange(100)] + [None]
        input2 = [Event(value=2, tag=2.0*i + 1.0) for i in xrange(100)] + [None]

        merge = Merge([q_in_1, q_in_2], q_out)
        merge.start()
        for val in input1:
            q_in_1.put(val)
        for val in input2:
            q_in_2.put(val)
        merge.join()
        for i in xrange(100):
            self.assertEquals(q_out.get().value, 1)
            self.assertEquals(q_out.get().value, 2)
        self.assertEquals(q_out.get(), None)

    def test_interleaving_merge(self):
        '''
        Test merging two channels that have different numbers of events, and 
        don't simply alternate their tags.
        '''
        q_in_1 = Channel()
        q_in_2 = Channel()
        q_out = Channel()

        input1 = [Event(value=1, tag=2.0*i) for i in xrange(3)] + [None]
        input2 = [Event(value=2, tag=0.5*i) for i in xrange(11)] + [None]

        merge = Merge([q_in_1, q_in_2], q_out)
        merge.start()
        for val in input1:
            q_in_1.put(val)
        for val in input2:
            q_in_2.put(val)
        merge.join()

        self.assertEquals(q_out.head().tag, 0.0)
        self.assertEquals(q_out.get().value, 1) # 0
        self.assertEquals(q_out.head().tag, 0.0)
        self.assertEquals(q_out.get().value, 2) # 0
        self.assertEquals(q_out.head().tag, 0.5)
        self.assertEquals(q_out.get().value, 2) # 0.5       
        self.assertEquals(q_out.head().tag, 1.0)
        self.assertEquals(q_out.get().value, 2) # 1.0
        self.assertEquals(q_out.head().tag, 1.5)
        self.assertEquals(q_out.get().value, 2) # 1.5  
        self.assertEquals(q_out.head().tag, 2.0)
        self.assertEquals(q_out.get().value, 1)   
        self.assertEquals(q_out.head().tag, 2.0)
        self.assertEquals(q_out.get().value, 2)
        self.assertEquals(q_out.head().tag, 2.5)
        self.assertEquals(q_out.get().value, 2)      
        self.assertEquals(q_out.head().tag, 3.0)
        self.assertEquals(q_out.get().value, 2)
        self.assertEquals(q_out.head().tag, 3.5)
        self.assertEquals(q_out.get().value, 2)   
        self.assertEquals(q_out.head().tag, 4.0)
        self.assertEquals(q_out.get().value, 1)
        self.assertEquals(q_out.head().tag, 4.0)
        self.assertEquals(q_out.get().value, 2)    
        self.assertEquals(q_out.head().tag, 4.5)
        self.assertEquals(q_out.get().value, 2)
        self.assertEquals(q_out.head().tag, 5.0)
        self.assertEquals(q_out.get().value, 2)         
        self.assertEquals(q_out.get(), None)


    def test_mass_merge(self):
        '''
        Test merging a large number (50) of input signals.
        '''
        num_input_channels, num_data_points = 50, 100

        input_channels = MakeChans(num_input_channels)
        output_channel = Channel()

        # Fill each channel with num_data_points of (channel, data) pairs,
        # then a None
        for i, input_channel in enumerate(input_channels):
            _ = [input_channel.put(Event(value=(i,j), tag=j)) for j in xrange(num_data_points)]
        _ = [input_channel.put(None) for input_channel in input_channels]

        merge = Merge(input_channels, output_channel)
        merge.start()
        merge.join()
        for i in xrange(num_data_points):
            for chan in xrange(num_input_channels):
                self.assertEquals(output_channel.get().value, (chan, i))
        self.assertEquals(output_channel.get(), None)


if __name__ == "__main__":
    #unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(MergeTests)
    unittest.TextTestRunner(verbosity=4).run(suite)

