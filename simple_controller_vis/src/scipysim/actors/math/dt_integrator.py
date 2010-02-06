'''
Created on 9/12/2009

@author: brian
'''
from scipysim.actors import Actor, Channel, Siso

class DTIntegrator(Siso):
    '''
    This is the docs for an instance of a DTIntegrator
    '''
    
    input_domains = ("DT",)
    output_domains = ("DT",)
    
    def __init__(self, input_queue, output_queue):
        '''
        Constructor for the running sum integrator actor. 
        '''
        super(DTIntegrator, self).__init__(input_queue=input_queue,
                                  output_queue=output_queue)
        self.sum = 0

    def siso_process(self, obj):
        self.sum += obj['value'] 
        obj['value'] = self.sum
        return obj


import unittest
class DTIntegratorTests(unittest.TestCase):
    '''Test the simple integrator actor'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = Channel()
        self.q_out = Channel()

    def test_positive_integers(self):
        '''Test running sum of a simple positive integer signal.
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
