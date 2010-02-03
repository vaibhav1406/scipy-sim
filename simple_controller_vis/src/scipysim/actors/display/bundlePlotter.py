'''
This plotting actor creates an output image (png) and optionally opens it.
Since static images don't animate very well it gets all the input at once in a "bundle".

@see multiple_summation_r... for a model which uses both dynamic and static plots.
@see noisy_ramp_plot for a model which uses just this static plot.

@author: brianthorne
'''

from models.actors.buffer import Bundle
from models.actors import Actor, DisplayActor, Channel

import numpy

import logging

import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure



class BundlePlotter(DisplayActor):
    '''
    A plot that is NOT dynamic. It takes a packet or bundle of events
    and plots it all at once.
    '''
    def __init__(self, input_queue, title="ScipySim"):
        super(BundlePlotter, self).__init__(input_queue=input_queue)
        self.title = title
        
    def process(self):
        self.data = self.input_queue.get(True)     # this is blocking
        if self.data is None:
            self.stop = True
        else:
            self.plot()
            
    def plot(self):
        self.x_axis_data = self.data["Tag"]
        self.y_axis_data = self.data["Value"]
        logging.info("Creating static plot of %d items" % len(self.data))
        
        f = Figure()
        canvas = FigureCanvas(f)
        
        a = f.add_subplot(111)
        a.plot(self.x_axis_data, self.y_axis_data)
        a.set_title(self.title)
        a.grid(True)
        
        # This creates a png image in the current directory
        canvas.print_figure(self.title, dpi=80) 
        logging.info("Saved output png image.")
        import webbrowser
        import os
        url = "file://" + os.getcwd() + "/" + self.title + ".png"
        logging.info("Image was saved at %s" % url)
        webbrowser.open_new_tab(url)

            
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