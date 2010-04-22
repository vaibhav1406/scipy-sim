'''
Created on 1/12/2009

@author: brian

Notes

How do we deal with "weird" input signals... what about random time intervals in DE?
Incompatible input/output frequencies...?
'''
from scipysim.actors import Siso, Actor, Channel, InvalidSimulationInput
import logging
import unittest
from numpy import linspace


class Sampler(Siso):
    '''
    This actor takes a source and samples it at a set frequency.
    The source must be at a equal or higher frequency that the desired output
    @see actors.interpolate
    '''
    def __init__(self, input_channel, output_channel, frequency=0.5):
        """
        Constructor for a down sampler.
        
        @param frequency: The desired signal output frequency, must be a factor of the input frequency
        """
        super(Sampler, self).__init__(input_channel=input_channel, output_channel=output_channel, child_handles_output=True)
        self.output_frequency = frequency
        self.output_period = 1.0 / frequency
        self.has_data = False
        self.last_point = None

    def siso_process(self, obj):
        logging.debug("Running sampler process")
        tag, value = obj['tag'], obj['value']

        logging.debug("Sampling received (tag: %2.e, value: %2.e )" % (tag, value))
        if not self.has_data or self.last_point['tag'] + self.output_period == obj['tag']:
            # This must be either the first data point or the next data point for given frequency
            self.last_point = obj
            self.has_data = True
            self.output_channel.put(obj)

        return

class SamplerTests(unittest.TestCase):
    '''Test the sampling actor'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = Channel("DT")
        self.q_out = Channel("CT")

    def test_basic_integer_tags(self):
        '''Test halving the frequency we sample a simple integer signal.
        
        Create a discrete time signal with a 1hz frequency and down-sample to 0.5hz
        '''
        inp = [{'value':1, 'tag':i} for i in xrange(0, 100, 1)]

        expected_outputs = [{'value':1, 'tag':i} for i in xrange(0, 100, 2)]

        down_sampler = Sampler(self.q_in, self.q_out, 0.5)
        down_sampler.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        down_sampler.join()

        for expected_output in expected_outputs:
            out = self.q_out.get()
            self.assertEquals(out['value'], expected_output['value'])
            self.assertEquals(out['tag'], expected_output['tag'])
        self.assertEquals(self.q_out.get(), None)

    def test_compatible_signals(self):
        '''Test reducing the frequency of a more complicated signal.
        Create a signal of 120 seconds, with 10 samples per second. (10hz)
        Down-sample this to a 2hz signal.
        '''
        simulation_time = 120   # seconds to simulate
        resolution = 10.0         # samples per second (10hz)
        desired_resolution = 2  # what we want out - (2hz)

        # Create tags for a signal from 0 to 120 seconds. 
        # length = number of seconds * ( samples per second + 1)
        freq = simulation_time * resolution
        tags = linspace(0, simulation_time , (freq) + 1)

        # Create 120 seconds of a discrete time signal with a 10hz frequency
        inp = [{'value':1, 'tag':i} for i in tags]

        step = resolution / desired_resolution
        expected_output = [ {'value':1, 'tag':i} for i in tags[::step]]

        down_sampler = Sampler(self.q_in, self.q_out, desired_resolution)
        down_sampler.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        down_sampler.join()

        for expected_output_element in expected_output:
            out = self.q_out.get()
            self.assertEquals(out['value'], expected_output_element['value'])
            self.assertEquals(out['tag'], expected_output_element['tag'])
        self.assertEquals(self.q_out.get(), None)

    def test_incompatible_signals(self):
        '''Test reducing the frequency by non integer factor.
        
        First create a signal of 120 seconds, with 10 samples per second.
        Down-sample this to a 8hz signal.
        '''
        simulation_time = 120   # seconds to simulate
        resolution = 10.0         # samples per second (10hz)
        desired_resolution = 8 # what we want out - (8hz)

        # Create tags for a signal from 0 to 120 seconds. 
        # length = number of seconds * ( samples per second + 1)
        freq = simulation_time * resolution
        tags = linspace(0, simulation_time , (freq) + 1)

        # Create 120 seconds of a discrete time signal with a 10hz frequency
        inp = [{'value':1, 'tag':i} for i in tags]

        down_sampler = Sampler(self.q_in, self.q_out, desired_resolution)
        down_sampler.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        down_sampler.join()

        out = self.q_out.get()
        # @todo: NEED TO WORK OUT HOW WE WANT TO DO THIS...
        self.assertEquals(type(out), InvalidSimulationInput)
        self.assertEquals(self.q_out.get(), None)

if __name__ == "__main__":
    unittest.main()
