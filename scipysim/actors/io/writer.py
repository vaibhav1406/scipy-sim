'''
Created on Feb 1, 2010

@author: brianthorne
'''

from scipysim.actors import Actor
from scipysim.actors import Channel
import numpy

class Writer(Actor):
    '''
    This Actor writes tagged signal data to a file.
    It uses numpy to write a binary file, first it gets all the input
    So make sure the signal can fit in memory!
    '''
    num_outputs = 0
    num_inputs = 1

    def __init__(self, input_channel, file_name="./signal_data.dat"):
        '''
        Constructor for a File Writer Actor
        '''
        super(Writer, self).__init__(input_channel=input_channel)
        self.filename = file_name
        self.temp_data = []

    def process(self):
        obj = self.input_channel.get(True)     # this is blocking
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
                                'formats': ['f8', 'f8'],
                                'titles': ['Domain', 'Name']    # This might not get used...
                             }
                        )
        x[:-1] = [ (element['tag'], element['value']) for element in self.temp_data if element is not None]

        numpy.save(self.filename, x)
