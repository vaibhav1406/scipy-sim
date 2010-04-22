'''
Created on Feb 1, 2010

@author: brianthorne
'''
from scipysim.actors import Source, Channel
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
    def __init__(self, output_channel, file_name):
        super(Reader, self).__init__(output_channel=output_channel)
        self.filename = file_name

    def process(self):
        x = numpy.load(self.filename)
        [self.output_channel.put({"tag": tag, 'value': value}) for (tag, value) in x]
        self.output_channel.put(None)
        self.stop = True


class TextReader(Source):
    '''This source creates string objects from a file.
    
    '''
    def __init__(self, output_channel, filename, send_as_words=False):
        '''A TextReader requires a valid filename to read from.
        The data may be sent as lines or words, lines are the
        default. The tag is the line number.
        '''
        super(TextReader, self).__init__(output_channel=output_channel)
        self.file = open(filename, 'r')
        self.send_as_words = send_as_words

    def process(self):
        for i, line in enumerate(self.file):
            if self.send_as_words:
                [self.output_channel.put({"tag": i, 'value': word.strip()}) for j, word in enumerate(line.split())]
            else:
                self.output_channel.put({"tag": i, 'value': line.strip()})
        self.output_channel.put(None)
        self.stop = True



