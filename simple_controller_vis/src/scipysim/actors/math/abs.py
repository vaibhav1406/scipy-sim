'''
Created on 9/12/2009

@author: brian
'''
from siso import Siso
import Queue as queue
import unittest

class Abs(Siso):
    '''
    This actor takes a source and passes on the absolute value. 
    '''
    def __init__(self, input_queue, output_queue):
        '''
        Constructor for the absolute actor. 
        '''
        super(Abs, self).__init__(input_queue=input_queue,
                                  output_queue=output_queue)

    def siso_process(self, obj):
        if obj['value'] < 0:
            obj['value'] *= -1
        return obj

class AbsTests(unittest.TestCase):
    '''Test the absolute actor'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = queue.Queue()
        self.q_out = queue.Queue()

    def test_positive_integers(self):
        '''Test a simple positive integer signal.
        '''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 100, 1)]

        expected_outputs = inp[:]

        abs = Abs(self.q_in, self.q_out)
        abs.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        abs.join()

        for expected_output in expected_outputs:
            out = self.q_out.get()
            self.assertEquals(out['value'], expected_output['value'])
            self.assertEquals(out['tag'], expected_output['tag'])
        self.assertEquals(self.q_out.get(), None)
