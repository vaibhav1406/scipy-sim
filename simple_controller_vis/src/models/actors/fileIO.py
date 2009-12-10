'''
Created on Dec 11, 2009

@author: brianthorne
'''
from Actor import Actor

class WriteDataFile(Actor):
    '''
    This Actor writes tagged signal data to a file.
    It uses numpy to write a binary file
    '''


    def __init__(self, input_queue, file_name="./signal_data.dat"):
        '''
        Constructor for a File Writer Actor
        '''
        super(WriteDataFile, self).__init__(input_queue=input_queue)
        self.filename = file_name

class ReadDataFile(Actor):
    '''
    This Actor reads a tagged signal from a file.
    The data must have been saved with the WriteFile Actor
    NOT CSV
    '''
    def __init__(self, output_queue, file_name="./signal_data.dat"):
        super(ReadDataFile, self).__init__(output_queue=output_queue)
        self.filename = file_name
    
        