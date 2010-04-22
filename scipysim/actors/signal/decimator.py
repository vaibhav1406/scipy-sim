'''
Created on 1/12/2009

@author: brian
'''
from scipysim.actors import Siso, Channel
import unittest

class Decimator(Siso):
    '''
    This actor takes a source and only passes on every Nth value
    '''
    def __init__(self, input_channel, output_channel, reduction_factor=5):
        '''
        Constructor for a decimation actor. 
        This actor is designed for even spaced inputs, 
        although it could "thin" a discrete events system.
        
        @param reduction: Keep every Nth sample, reduces the signal by factor passed in.
        '''
        super(Decimator, self).__init__(input_channel=input_channel,
                                        output_channel=output_channel,
                                        child_handles_output=True)

        self.reduction_factor = int(reduction_factor)
        self.sample = 0

    def siso_process(self, obj):

        if self.sample % self.reduction_factor == 0:
            self.output_channel.put(obj)
        self.sample += 1

class DecimatorTests(unittest.TestCase):
    '''Test the decimation actor'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = Channel()
        self.q_out = Channel()

    def test_basic_integer_tags(self):
        '''Test halving the frequency we sample a simple integer signal.
        
        Create a discrete time signal with a 1hz frequency 
        down-sample to 0.5hz by a factor 2 reduction
        '''
        inp = [{'value':1, 'tag':i} for i in xrange(0, 100, 1)]

        expected_outputs = [{'value':1, 'tag':i} for i in xrange(0, 100, 2)]

        down_sampler = Decimator(self.q_in, self.q_out, 2)
        down_sampler.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        down_sampler.join()

        for expected_output in expected_outputs:
            out = self.q_out.get()
            self.assertEquals(out['value'], expected_output['value'])
            self.assertEquals(out['tag'], expected_output['tag'])
        self.assertEquals(self.q_out.get(), None)

if __name__ == "__main__":
    unittest.main()
