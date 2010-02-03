'''
Created on Feb 1, 2010

@author: brianthorne
'''
from scipysim.actors import Source
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
    

class TextReader(Source):
    '''This source creates string objects from a file.
    
    '''
    def __init__(self, output_queue, filename, send_as_words=False):
        '''A TextReader requires a valid filename to read from.
        The data may be sent as lines or words, lines are the
        default
        '''
        super(TextReader, self).__init__(output_queue=output_queue)
        self.file = open(filename, 'r')
        self.send_as_words = send_as_words
   
    def process(self):
        for i,line in enumerate(self.file):
            if self.send_as_words:
                [self.output_queue.put({"tag": i*j,'value': word.strip()}) for j, word in enumerate(line.split())]
            else:
                self.output_queue.put({"tag": i,'value': line.strip()})
        self.output_queue.put(None)
        self.stop = True
            
from scipysim.actors import Channel
def test_text_reader():
    filename = "reader.py"
    output = Channel()
    reader = TextReader(output, filename, send_as_words=True)
    reader.start()
    reader.join()
    print output.get()
    print output.get()

if __name__ == "__main__":
    test_text_reader()

    
    