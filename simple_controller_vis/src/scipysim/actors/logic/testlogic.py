'''
Created on Feb 2, 2010

@author: brianthorne
'''
import unittest
from scipysim.actors import SisoTestHelper, Channel
import numpy
from scipysim.actors.logic import GreaterThan, LessThan, PassThrough


class PassThroughTests(unittest.TestCase):
    '''Test the IF actor'''
    def setUp(self):
        '''General set up that will be used in all tests'''
        self.data_in = Channel()
        self.bool_in = Channel()
        self.output = Channel()

        # Some fake boolean data
        self.every_second_point = [True, False] * 50
        self.no_points = [False] * 100

        # some fake pass through data, and add it to the channel
        self.data = range(100)
        [self.data_in.put({'tag':i, 'value':i}) for i in range(100)]
        self.data_in.put(None)

        # create the block
        self.block = PassThrough(self.bool_in, self.data_in, self.output)

    def test_all_points(self):
        '''Test that it passes through every point when given True control signal'''
        every_point = [True] * 100
        [self.bool_in.put({'tag':i, 'value':every_point[i]}) for i in self.data]
        self.bool_in.put(None)
        self.block.start()
        self.block.join()
        [self.assertEquals(self.output.get()['tag'], i) for i in self.data]
        self.assertEquals(None, self.output.get())

    def test_every_second_point(self):
        '''Test every second point is passed through
        and that the rest is discarded
        '''
        [self.bool_in.put(
                          {'tag':i, 'value':self.every_second_point[i]}
                         ) for i in self.data]
        self.bool_in.put(None)
        self.block.start()
        self.block.join()
        [self.assertEquals(self.output.get()['tag'],
                           i) for i in self.data if i % 2 == 0]
        self.assertEquals(None, self.output.get())


    def test_no_points(self):
        '''Test that no points get passed through for an all False signal'''
        [self.bool_in.put(
                          {'tag':i,
                           'value':self.no_points[i]
                           }) for i in self.data]
        self.bool_in.put(None)
        self.block.start()
        self.block.join()
        self.assertEquals(None, self.output.get())

class ElsePassThroughTests(unittest.TestCase):
    '''Test the IF-Else actor'''
    def setUp(self):
        '''General set up that will be used in all tests'''
        self.data_in = Channel()
        self.alt_data_in = Channel()
        self.bool_in = Channel()
        self.output = Channel()

        # Some fake boolean data
        self.every_second_point = [True, False] * 50

        # some fake pass through data, and add it to the channel
        self.data = range(100)
        self.data_alt = 10 * self.data
        [self.alt_data_in.put(
                              {'tag':i, 'value':self.data_alt[i]}
                              ) for i in range(100)]
        [self.data_in.put({'tag':i, 'value':i}) for i in range(100)]
        self.data_in.put(None)
        self.alt_data_in.put(None)

        # create the block
        self.block = PassThrough(self.bool_in,
                                 self.data_in,
                                 self.output,
                                 else_data_input=self.alt_data_in)

    def test_every_second_alternative(self):
        '''Test merging with if - else actor.
        half the values come from one channel, and half from the other'''
        [self.bool_in.put(
                          {'tag':i, 'value':self.every_second_point[i]}
                         ) for i in self.data]
        self.bool_in.put(None)
        self.block.start()
        self.block.join()
        for i in self.data:
            output = self.output.get(True)
            self.assertEquals(output['tag'], i)
            if i % 2 == 0:
                self.assertEquals(output['value'], i)
            else:
                self.assertEquals(output['value'], self.data_alt[i])
        self.assertEquals(None, self.output.get())

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
        SisoTestHelper(self, less_than_block, inp, expected_outputs)

    def test_greater_than_positive_integers(self):
        '''Test a simple positive integer signal.
        '''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 100, 1)]
        expected_outputs = [i for i in inp if i['value'] >= 50]
        greater_than_block = GreaterThan(self.q_in, self.q_out, 50)
        SisoTestHelper(self, greater_than_block, inp, expected_outputs)

    def test_boolean_output(self):
        '''Test thresholding a signal into a binary signal'''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 100, 1)]
        expected_outputs = [{'value': True if i['value'] >= 50 else False, 'tag': i['tag']} for i in inp ]
        block = GreaterThan(self.q_in, self.q_out, 50, True)
        SisoTestHelper(self, block, inp, expected_outputs)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
