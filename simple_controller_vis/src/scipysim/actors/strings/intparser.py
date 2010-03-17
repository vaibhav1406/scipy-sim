'''
Created on Feb 2, 2010

@author: brianthorne
'''
from scipysim.actors import Siso
import logging

class IntParser(Siso):
    '''
    Takes a tagged string input and if possible converts into integers.
    '''

    def __init__(self, input_channel, output_channel):
        super(IntParser, self).__init__(input_channel=input_channel,
                                        output_channel=output_channel,
                                        child_handles_output=True)

    def siso_process(self, obj):
        obj['value'] = int(obj['value'])
        self.output_channel.put(obj)
        #logging.warn("Probably just broke something... tried to parse string to int but failed")

import unittest
from scipysim.actors import Channel
from scipysim.actors import SisoTestHelper
class IntParserTests(unittest.TestCase):

    def setUp(self):
        self.q_in = Channel()
        self.q_out = Channel()

    def test_basic(self):
        inputs = [{'value':str(i), 'tag':i} for i in xrange(10)]
        expected_outputs = [{'value':int(i), 'tag':i} for i in xrange(10)]
        block = IntParser(self.q_in, self.q_out)
        SisoTestHelper(self, block, inputs, expected_outputs)

if __name__ == '__main__':
    unittest.main()
