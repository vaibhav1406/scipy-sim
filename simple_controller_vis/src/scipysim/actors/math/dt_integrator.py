'''
Created on 9/12/2009

@author: brian
'''
from Actor import Actor, Channel
from siso import Siso

from model import Model
from copier import Copier
from summer import Summer
from delay import Delay
import Queue as queue
class RunningSum(Siso):
    def __init__(self, in_chan, out_chan):
        super(RunningSum, self).__init__(in_chan, out_chan)
        self.delay = Delay()
        self.feedback = Channel()
        self.out = Channel()
        self.outputCloner = Copier(self.out, [self.output_queue, self.feedback])
        self.summer = Summer([in_chan, self.feedback])
        # This could be made up of smaller blocks... but why?

class DTIntegrator(Siso):
    '''
    This 
    '''
    def __init__(self, input_queue, output_queue):
        '''
        Constructor for the running sum actor. 
        '''
        super(DTIntegrator, self).__init__(input_queue=input_queue,
                                  output_queue=output_queue)
        self.sum = 0

    def siso_process(self, obj):
        self.sum += obj['value'] 
        obj['value'] = self.sum
        return obj


import unittest

class AbsTests(unittest.TestCase):
    '''Test the simple integrator actor'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = queue.Queue()
        self.q_out = queue.Queue()

    def test_positive_integers(self):
        '''Test a simple positive integer signal.
        '''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 10, 1)]

        expected_output_values = [sum(range(i)) for i in xrange(1,11)]

        block = DTIntegrator(self.q_in, self.q_out)
        block.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        block.join()

        for expected_output in expected_output_values:
            out = self.q_out.get()
            self.assertEquals(out['value'], expected_output)
        self.assertEquals(self.q_out.get(), None)
