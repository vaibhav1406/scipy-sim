'''
Created on Dec 11, 2009

@author: brianthorne
'''

from models.actors import Channel
from models.actors.io import Reader, Writer
import Queue as queue
import numpy

import unittest
import tempfile

class FileIOTests(unittest.TestCase):
    '''Test the FileIO Actors'''
    
    def setUp(self):
        self.chan = Channel()
        self.signal = [{'value':i**3, 'tag':i} for i in xrange(100)] + [None]
        [self.chan.put(val) for val in self.signal]   
        self.f = tempfile.NamedTemporaryFile()#delete=False)
        
    def tearDown(self):
        self.f.close()
        
        
    def test_file_write(self):
        '''Test that we can save data'''
        fileWriter = Writer(self.chan, self.f.name)
        fileWriter.start()
        fileWriter.join()
        # Check that the queue has been emptied...
        self.assertRaises(queue.Empty, self.chan.get, timeout=1)
        
    
    def test_file_read(self):
        fileName = '/Users/brianthorne/temp/numpy_test_data.npy'
        
        fileWriter = Writer(self.chan, fileName)
        fileWriter.start()
        fileWriter.join()

                
        fileReader = Reader(output_queue=self.chan, file_name=fileName)
        fileReader.start()
        fileReader.join()
        
        for expected in self.signal:
            if expected is not None:
                received = self.chan.get()
                self.assertEqual(received['tag'], expected['tag'])
                self.assertEqual(received['value'], expected['value'])
        self.assertEqual(expected, None)

        
if __name__ == "__main__":
    unittest.main()
           