'''
Created on Dec 11, 2009

@author: brianthorne
'''

from scipysim.actors import Channel
from scipysim.actors.io import Reader, Writer, Bundle, Unbundle
from scipysim.actors.io import TextReader
import Queue as queue
import numpy

import unittest
import tempfile
import os
PATH_TO_THIS_FILE = __file__.replace('.pyc', '.py') # Make sure we don't get the compiled file

class TestReader(unittest.TestCase):

    def test_text_reader(self):
        filename = PATH_TO_THIS_FILE
        output = Channel()
        reader = TextReader(output, filename, send_as_words=True)
        reader.start()
        reader.join()
        self.assertEquals("'''", output.get()['value'])
        self.assertEquals(1, output.get()['tag'])


class FileIOTests(unittest.TestCase):
    '''Test the FileIO Actors'''

    def setUp(self):
        self.chan = Channel()
        self.signal = [{'value':i ** 3, 'tag':i} for i in xrange(100)] + [None]
        [self.chan.put(val) for val in self.signal]
        self.f = tempfile.NamedTemporaryFile()#delete=False)

    def tearDown(self):
        self.f.close()


    def test_file_write(self):
        '''Test that we can save data'''
        fileWriter = Writer(self.chan, self.f.name)

        # Run the file writer and save the output to a temp file
        fileWriter.start()
        fileWriter.join()

        # Check that the channel is empty...
        self.assertRaises(queue.Empty, self.chan.get_nowait)


    def test_file_read(self):
        '''Test that we can retrieve data'''
        # Using self.f here, even with delete set to false, doesn't seem to
        # work. So we need to manually create a temp file.
        fileName = tempfile.gettempdir() + '/numpy_test_data.npy'

        fileWriter = Writer(self.chan, fileName)
        fileWriter.start()
        fileWriter.join()

        fileReader = Reader(output_channel=self.chan, file_name=fileName)
        fileReader.start()
        fileReader.join()

        for expected in self.signal:
            if expected is not None:
                received = self.chan.get()
                self.assertEqual(received['tag'], expected['tag'])
                self.assertEqual(received['value'], expected['value'])
        self.assertEqual(expected, None)
        os.remove(fileName) # clean up

class BundleTests(unittest.TestCase):
    def setUp(self):
        self.q_in = Channel()
        self.q_out = Channel()
        self.q_out2 = Channel()
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
