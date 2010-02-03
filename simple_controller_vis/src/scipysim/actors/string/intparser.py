'''
Created on Feb 2, 2010

@author: brianthorne
'''
from scipysim.actors import Siso

class IntParser(Siso):
    '''
    Takes a tagged string input and if possible converts into integers.
    '''

    def __init__(self, input_queue, output_queue, child_handles_output=True):
        super(IntParser, self).__init__(input_queue=input_queue,
                                  output_queue=output_queue)

    def siso_process(self, obj):
        try:
            obj['value'] = int(obj['value'])
            self.output_queue.put(obj)
        except:
            pass
        
import unittest
from scipysim.actors import Channel
from scipysim.actors.siso import TestSisoActor
class TestIntParser(unittest.TestCase):
    
    def setUp(self):
        self.q_in = Channel()
        self.q_out = Channel()
    
    def test_basic(self):
        inputs = [{'value':str(i), 'tag':i} for i in xrange(10)]
        expected_outputs = [{'value':int(i), 'tag':i} for i in xrange(10)]
        block = IntParser(self.q_in, self.q_out)
        TestSisoActor(self, block, inputs, expected_outputs)
        
if __name__ == '__main__':
    unittest.main()