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
        if obj.last:
            self.write_file()
            self.stop = True
            return
        else:
            self.temp_data.append(obj)


    def write_file(self):
        x = numpy.zeros(len(self.temp_data)+1,
                            dtype=
                            {
                                'names': ["Tag", "Value"],
                                'formats': ['f8', 'f8'],
                                'titles': ['Domain', 'Name']    # This might not get used...
                             }
                        )
        x[:-1] = [ (element['tag'], element['value']) for element in self.temp_data]

        numpy.save(self.filename, x)

class TextWriter(Actor):
    '''This Actor creates text files out of string objects.
    
    '''
    num_outputs = 0
    num_inputs = 1
    
    def __init__(self, input_channel, filename):
        '''
        A TextWriter requires a valid filename to write to as well as
        permission to write to that file.

        The tag is written first, followed by a comma, a single space then the value.
        '''
        super(TextWriter, self).__init__(input_channel=input_channel)
        self.filename = filename
        self.temp_data = []

    def process(self):
        obj = self.input_channel.get(True)     # this is blocking
        if obj.last:
            self.write_file()
            self.stop = True
            return
        else:
            self.temp_data.append(obj)

    def write_file(self):
        f = open(self.filename, 'w')
        content = '\n'.join(['%s, %s' % (event.tag, event.value) for event in self.temp_data])
        f.writelines(content)
        f.close()
        
