
import logging
from models.actors import Actor
import Queue as queue

import unittest
import numpy

class Bundle(Actor):
    '''
    This buffering/compressing/bundling actor takes a source 
    and waits for a preset number 
    of events (or for the signal to finish) before passing them on in one.
    
    They get passed on as a special condensed packet.
    '''

    def __init__(self, input_queue, output_queue, bundle_size=None):
        """
        Constructor for a bundle block.

        @param input_queue: The input queue to be bundled

        @param output_queue: The output queue that has been bundled

        @param bundle_size: The max size of an output bundle. Default
        is to buffer the whole signal then output a single bundle.
        """
        super(Bundle, self).__init__(input_queue=input_queue, output_queue=output_queue)
        self.bundle_size = bundle_size
        self.temp_data = []

    def process(self):
        """Send packets of events at one time"""
        logging.debug("Running buffer/bundle process")
        obj = self.input_queue.get(True)     # this is blocking
        if obj is not None:
            self.temp_data.append(obj)
        if obj is None or self.bundle_size is not None and len(self.temp_data) >= self.bundle_size:
            self.send_bundle()

            if obj is None:
                self.output_queue.put(None)
                self.stop = True
            else:
                self.temp_data = []
            
    def send_bundle(self):
        '''Create a numpy data type that can carry all the i
        nformation then add it to the output queue'''
        x = numpy.zeros(len(self.temp_data),
                            dtype=
                            {
                                'names': ["Tag", "Value"],
                                'formats': ['f8','f8'],
                                'titles': ['Domain', 'Name']    # This might not get used...
                             }
                        )
        x[:] = [ ( element['tag'], element['value'] ) for element in self.temp_data if element is not None]
        self.output_queue.put(x)

class Unbundle(Actor):
    '''Given a bundled source, recreate the queue that made it'''
    
    def __init__(self, input_queue, output_queue):
        super(Unbundle, self).__init__(input_queue=input_queue, output_queue=output_queue)

    def process(self):
        x = self.input_queue.get(True)
        if x is not None:
            [self.output_queue.put({"tag": tag,'value': value}) for (tag,value) in x]
        else:
            self.output_queue.put(None)
            self.stop = True
        
class BundleTests(unittest.TestCase):
    def setUp(self):
        self.q_in = queue.Queue()
        self.q_out = queue.Queue()
        self.q_out2 = queue.Queue()
        self.input = [{'value': 1, 'tag': i } for i in xrange(100)]

    def tearDown(self):
        del self.q_in
        del self.q_out

    def test_bundle_full_signal(self):
        '''Test sending a basic integer tagged signal all at once'''
        bundle_size = 1000

        
        #expected_output = [{'value':1, 'tag': i + delay } for i in xrange(100)]

        block = Bundle(self.q_in, self.q_out, bundle_size)
        block.start()
        [self.q_in.put(i) for i in self.input + [None]]

        block.join()
        actual_output = self.q_out.get()
        self.assertEqual(actual_output.size, 100) 
        self.assertEquals(None, self.q_out.get())
        
    def test_bundle_partial_signal(self):
        '''Test sending a basic integer tagged signal in sections'''
        bundle_size = 40

        
        #expected_output = [{'value':1, 'tag': i + delay } for i in xrange(100)]

        block = Bundle(self.q_in, self.q_out, bundle_size)
        block.start()
        [self.q_in.put(i) for i in self.input + [None]]

        block.join()
        actual_output = self.q_out.get()
        self.assertEqual(actual_output.size, bundle_size) 
        actual_output = self.q_out.get()
        self.assertEqual(actual_output.size, bundle_size)
        actual_output = self.q_out.get()
        self.assertEqual(actual_output.size, 20)
        self.assertEquals(None, self.q_out.get())
        
    def test_unbundle(self):
        '''Test the unbundler and the bundler'''
        bundler = Bundle(self.q_in, self.q_out)
        unbundler = Unbundle(self.q_out, self.q_out2)
        [block.start() for block in [bundler, unbundler]]
        [self.q_in.put(i) for i in self.input + [None]]
        [block.join() for block in [bundler, unbundler]]
        [self.assertEquals(self.q_out2.get(), i) for i in self.input]
        self.assertEqual(self.q_out2.get(), None)
        
if __name__ == "__main__":
    unittest.main()
