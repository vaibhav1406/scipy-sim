'''
Created on Dec 11, 2009

@author: brianthorne
'''
from Actor import Actor, Channel
import Queue as queue
import numpy

import unittest
class WriteDataFile(Actor):
    '''
    This Actor writes tagged signal data to a file.
    It uses numpy to write a binary file, first it gets all the input
    So make sure the signal can fit in memory!
    '''


    def __init__(self, input_queue, file_name="./signal_data.dat"):
        '''
        Constructor for a File Writer Actor
        '''
        super(WriteDataFile, self).__init__(input_queue=input_queue)
        self.filename = file_name
        self.temp_data = []
        
    def process(self):
        obj = self.input_queue.get(True)     # this is blocking
        self.temp_data.append(obj)
        if obj is None:
            self.write_file()
            self.stop = True
            return
        
    def write_file(self):
        x = numpy.zeros(len(self.temp_data),
                            dtype=
                            {
                                'names': ["Tag", "Value"],
                                'formats': ['f8','f8'],
                                'titles': ['Domain', 'Name']    # This might not get used...
                             }
                        )
        x[:-1] = [ ( element['tag'], element['value'] ) for element in self.temp_data if element is not None]
        
        numpy.save(self.filename, x)

class ReadDataFile(Actor):
    '''
    This Actor reads a tagged signal from a file - the signal can be any
    domain - the data for both tags and values are stored as 64bit floats.
    The data must have been saved with the WriteFile Actor NOT CSV.
    
    The numpy structured record array is as follows: 
                            dtype=
                            {
                                'names': ["Tag", "Value"],
                                'formats': ['f8','f8'],
                                'titles': ['Domain', 'Name']
                             }
    Note the titles may be used to store domain and signal name information.
    '''
    def __init__(self, output_queue, file_name):
        super(ReadDataFile, self).__init__(output_queue=output_queue)
        self.filename = file_name
    
    def process(self):
        x = numpy.load(self.filename)
        [self.output_queue.put({"tag": tag,'value': value}) for (tag,value) in x]
        self.output_queue.put(None)
        self.stop = True
            
import unittest
import tempfile
class FileIOTests(unittest.TestCase):
    '''Test the Proportional Actor'''
    
    def setUp(self):
        self.chan = Channel()
        self.signal = [{'value':i**3, 'tag':i} for i in xrange(100)] + [None]
        [self.chan.put(val) for val in self.signal]   
        self.f = tempfile.NamedTemporaryFile(delete=False)
        
    def tearDown(self):
        self.f.close()
        
        
    def test_file_write(self):
        '''Test that we can save data'''
        fileWriter = WriteDataFile(self.chan, self.f.name)
        fileWriter.start()
        fileWriter.join()
        # Check that the queue has been emptied...
        self.assertRaises(queue.Empty, self.chan.get, timeout=1)
        
    
    def test_file_read(self):
        fileName = '/Users/brianthorne/temp/numpy_test_data.npy'
        
        fileWriter = WriteDataFile(self.chan, fileName)
        fileWriter.start()
        fileWriter.join()

                
        fileReader = ReadDataFile(output_queue=self.chan, file_name=fileName)
        fileReader.start()
        fileReader.join()
        
        [self.assertEquals(self.chan.get(), i) for i in self.signal]
        
        self.f.delete()
        
        