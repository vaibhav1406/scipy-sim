'''
Created on Feb 1, 2010
@see multiple_summation... for a use.
@author: brianthorne
'''
from models.actors.buffer import Bundle
from models.actors import DisplayActor, Channel
import numpy

import matplotlib.pyplot as plt

class BundlePlotter(DisplayActor):
    '''
    A plot that is NOT dynamic. It takes a packet or bundle of events
    and plots it all at once.
    '''
    def __init__(self, input_queue):
        super(BundlePlotter, self).__init__(input_queue=input_queue)
        #plt.figure()

        
    def process(self):
        self.data = self.input_queue.get(True)     # this is blocking
        
        if self.data is None:
            self.stop = True
        else:
            self.plot()
            
    def plot(self):
        self.x_axis_data = self.data["Tag"]
        self.y_axis_data = self.data["Value"]
        self.line, = plt.plot(self.x_axis_data, self.y_axis_data)
            
import unittest
class BundlePlotTests(unittest.TestCase):
    def setUp(self):
        self.q_in = Channel()
        self.q_out = Channel()
        self.q_out2 = Channel()
        self.input = [{'value': 1, 'tag': i } for i in xrange(100)]

    def tearDown(self):
        del self.q_in
        del self.q_out

    def test_getting_bundle_data(self):
        '''Test bundling a signal and getting the data back'''

        block = Bundle(self.q_in, self.q_out)
        block.start()
        [self.q_in.put(i) for i in self.input + [None]]
        block.join()
        bundled_data = self.q_out.get()
        self.assertEqual(len(bundled_data), 100)
        self.assertEqual(type(bundled_data), numpy.ndarray)
        values = bundled_data["Value"]
        self.assertTrue(all(values==1))
        tags = bundled_data["Tag"]
        [self.assertEquals(tags[i] ,i) for i in xrange(100 ) ]
       
    def test_plotting(self):
        bundler = Bundle(self.q_in, self.q_out)
        bundlingPlotter = BundlePlotter(self.q_out)
        [block.start() for block in [bundler, bundlingPlotter]]
        [self.q_in.put(i) for i in self.input + [None]]
        [block.join() for block in [bundler, bundlingPlotter]]

if __name__ == "__main__":
    unittest.main()