'''
Created on Dec 7, 2009

@author: brianthorne
'''
from Actor import Actor
class Model(Actor):
    '''
    A Model is a full citizen actor, it has its own thread of 
    control, it takes parameters and can have input and output 
    channels.
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    
    def process(self):
        '''
        The process function is called as often as possible by the threading or multitasking library
        No guarantees are made about timing, or that anything will have changed for the input queues
        '''
        raise NotImplementedError()