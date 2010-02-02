'''
Created on Feb 1, 2010

@author: brianthorne
'''
from models.actors import Source
import Queue as queue
import numpy

class Reader(Source):
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
    The data can be recovered as seperate arrays with data['Tag'] and data['Value']
    or it can be treated as a list of event tuples.
    '''
    def __init__(self, output_queue, file_name):
        super(Reader, self).__init__(output_queue=output_queue)
        self.filename = file_name
    
    def process(self):
        x = numpy.load(self.filename)
        [self.output_queue.put({"tag": tag,'value': value}) for (tag,value) in x]
        self.output_queue.put(None)
        self.stop = True
            