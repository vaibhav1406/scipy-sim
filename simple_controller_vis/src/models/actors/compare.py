from siso import Siso
from Actor import Channel
import unittest

class Compare(Siso):
    '''This abstract class carries out a comparison.
    '''
    def __init__(self, input_queue, output_queue, threshold, boolean_output=False):
        super(Compare, self).__init__(input_queue=input_queue,
                                      output_queue=output_queue,
                                      child_handles_output=True)
        self.bool_out = boolean_output
        self.threshold = threshold
        
    def compare(self, obj):
        '''This method must be overridden. If it returns True
        The value is put onto the output queue, 
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
    This actor takes a source and passes on the value if it is over a threshold. 
    
    @param boolean_output: If this is set to true, instead of passing on the value, 
    the value is replaced with a True value.
    '''
    def __init__(self, input_queue, output_queue, threshold, boolean_output=False):
        '''
        Constructor for the absolute actor. 
        '''
        super(GreaterThan, self).__init__(input_queue=input_queue,
                                          output_queue=output_queue,
                                          threshold=threshold,
                                          boolean_output=boolean_output)

    def compare(self, obj):
        return obj['value'] >= self.threshold

class CompareTests(unittest.TestCase):
    '''Test the comparison actor'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = Channel()
        self.q_out = Channel()

    def test_positive_integers(self):
        '''Test a simple positive integer signal.
        '''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 100, 1)]

        expected_outputs = [i for i in inp if i['value'] >= 50]

        block = GreaterThan(self.q_in, self.q_out, 50)
        block.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        block.join()

        for expected_output in expected_outputs:
            out = self.q_out.get()
            self.assertEquals(out['value'], expected_output['value'])
            self.assertEquals(out['tag'], expected_output['tag'])
        self.assertEquals(self.q_out.get(), None)

    def test_boolean_output(self):
        '''Test a thresholding a signal into a binary signal
        '''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 100, 1)]

        expected_outputs = [{'value': True, 'tag': i['tag']} for i in inp if i['value'] >= 50]


        block = GreaterThan(self.q_in, self.q_out, 50, True)
        block.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        block.join()

        for expected_output in expected_outputs:
            out = self.q_out.get()
            self.assertEquals(out['value'], expected_output['value'])
            self.assertEquals(out['tag'], expected_output['tag'])
        self.assertEquals(self.q_out.get(), None)