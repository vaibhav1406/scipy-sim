'''
Created on Dec 11, 2009

@author: brianthorne
'''

from scipysim.actors import Channel, Event, LastEvent
from scipysim.actors.io import Reader, Writer, Bundle, Unbundle
from scipysim.actors.io import TextReader, TextWriter
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
        self.assertEquals("'''", output.get().value)
        self.assertEquals(1, output.get().tag)

class TestTextWriter(unittest.TestCase):

    def test_text_writer(self):
        tfile = tempfile.NamedTemporaryFile()
        filename = tfile.name
        output = Channel()
        writer = TextWriter(output, filename)
        [output.put(e) for e in [Event(value=i ** 3, tag=i) for i in xrange(100)] + [LastEvent()]]
        writer.start()
        writer.join()

        for i, line in enumerate(tfile):
            self.assertEquals('%s, %s' % (str(i), str(i**3)), line.strip())
        
        

class FileIOTests(unittest.TestCase):
    '''Test the FileIO Actors'''

    def setUp(self):
        self.chan = Channel()
        self.signal = [Event(value=i ** 3, tag=i) for i in xrange(100)] + [LastEvent()]
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
        self.assertRaises(Channel.Empty, lambda: self.chan.get(block=False))

        # TODO check the data (load with numpy)

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
            if not expected.last:
                received = self.chan.get()
                self.assertEqual(received.tag, expected.tag)
                self.assertEqual(received.value, expected.value)
        self.assertTrue(expected.last)
        os.remove(fileName) # clean up

class BundleTests(unittest.TestCase):
    def setUp(self):
        self.q_in = Channel()
        self.q_out = Channel()
        self.q_out2 = Channel()
        self.input = [Event(value=1, tag=i) for i in xrange(100)]

    def tearDown(self):
        del self.q_in
        del self.q_out

    def test_bundle_full_signal(self):
        '''Test sending a basic integer tagged signal all at once'''
        bundle_size = 1000


        #expected_output = [Event(value=1, tag=i + delay) for i in xrange(100)]

        block = Bundle(self.q_in, self.q_out, bundle_size)
        block.start()
        [self.q_in.put(i) for i in self.input + [LastEvent()]]

        block.join()
        actual_output = self.q_out.get()
        self.assertEqual(actual_output.size, 100)
        self.assertTrue(self.q_out.get().last)

    def test_bundle_partial_signal(self):
        '''Test sending a basic integer tagged signal in sections'''
        bundle_size = 40


        #expected_output = [Event(value=1, tag=i + delay) for i in xrange(100)]

        block = Bundle(self.q_in, self.q_out, bundle_size)
        block.start()
        [self.q_in.put(i) for i in self.input + [LastEvent()]]

        block.join()
        actual_output = self.q_out.get()
        self.assertEqual(actual_output.size, bundle_size)
        actual_output = self.q_out.get()
        self.assertEqual(actual_output.size, bundle_size)
        actual_output = self.q_out.get()
        self.assertEqual(actual_output.size, 20)
        self.assertTrue(self.q_out.get().last)

    def test_unbundle(self):
        '''Test the unbundler and the bundler'''
        bundler = Bundle(self.q_in, self.q_out)
        unbundler = Unbundle(self.q_out, self.q_out2)
        [block.start() for block in [bundler, unbundler]]
        [self.q_in.put(i) for i in self.input + [LastEvent()]]
        [block.join() for block in [bundler, unbundler]]
        [self.assertEquals(self.q_out2.get(), i) for i in self.input]
        self.assertTrue(self.q_out2.get().last)

if __name__ == "__main__":
    unittest.main()
