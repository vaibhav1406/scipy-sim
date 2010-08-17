'''
Created on 9/12/2009

@author: brian
'''
from scipysim.actors import Siso

class Abs(Siso):
    '''
    This actor takes a source and passes on the absolute value. 
    '''
    def __init__(self, input_channel, output_channel):
        '''
        Constructor for the absolute actor. 
        '''
        super(Abs, self).__init__(input_channel=input_channel,
                                  output_channel=output_channel)

    def siso_process(self, obj):
        tag, value = obj['tag'], obj['value']
        if value < 0:
            value *= -1
        return { 'tag':tag, 'value':value }

