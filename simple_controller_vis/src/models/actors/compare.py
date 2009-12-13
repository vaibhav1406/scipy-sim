from siso import Siso, TestSisoActor
from Actor import Channel
import unittest
import numpy

class Compare(Siso):
    '''This abstract base class is for any actor which carries out a comparison.
    @requires: Compare function to take a dictionary object and return true/false.
    '''
    def __init__(self, input_queue, output_queue, threshold, boolean_output=False):
        '''Constructor for a Compare actor.
        
        @param threshold: Since most comparisons occur against something, this simply stores 
        the threshold value in self.threshold
        
        @param boolean_output: If this is set to true, instead of passing on 
        the value, the value is replaced with the boolean 'True' value.
        '''
        super(Compare, self).__init__(input_queue=input_queue,
                                      output_queue=output_queue,
                                      child_handles_output=True)
        self.bool_out = boolean_output
        self.threshold = threshold
        
    def compare(self, obj):
        '''This method must be overridden. If it returns True
        the value is put onto the output queue, 
        OR if boolean_output is true, a boolean is substituted for the 'value'
        
        @return Boolean value
        '''
        raise NotImplemented
    
    def siso_process(self, obj):
        if self.compare(obj):
            if self.bool_out:
                obj['value'] = True
            self.output_queue.put(obj)

class GreaterThan(Compare):
    '''
    This actor takes a source and passes on the value if it is equal or over 
    a specified threshold. 
    '''
    def compare(self, obj):
        return obj['value'] >= self.threshold

class LessThan(Compare):
    def compare(self, obj):
        return obj['value'] < self.threshold

class CompareTests(unittest.TestCase):
    '''Test the comparison actors'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = Channel()
        self.q_out = Channel()

    def test_less_than(self):
        '''Test a float valued less than comparison with boolean output.'''
        input_values = numpy.linspace(0, 100, 314)
        inp = [{'value':input_values[i], 'tag':i} for i in xrange(len(input_values))]
        expected_outputs = [i for i in inp if i['value'] < 50]
        less_than_block = LessThan(self.q_in, self.q_out, threshold=50)
        TestSisoActor(self, less_than_block, inp, expected_outputs)
  
    def test_greater_than_positive_integers(self):
        '''Test a simple positive integer signal.
        '''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 100, 1)]
        expected_outputs = [i for i in inp if i['value'] >= 50]
        greater_than_block = GreaterThan(self.q_in, self.q_out, 50)
        TestSisoActor(self, greater_than_block, inp, expected_outputs)
        
    def test_boolean_output(self):
        '''Test a thresholding a signal into a binary signal
        '''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 100, 1)]
        expected_outputs = [{'value': True, 'tag': i['tag']} for i in inp if i['value'] >= 50]
        block = GreaterThan(self.q_in, self.q_out, 50, True)
        TestSisoActor(self, block, inp, expected_outputs)
        