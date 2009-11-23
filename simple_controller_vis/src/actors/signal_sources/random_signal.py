'''
Created on 19/11/2009

@author: brian
'''

class Source(object):
    '''
    This is just an abstract interface for a signal source.
    '''

    def __init__(self):
        raise NotImplementedError("This base class is supposed to be derived from")
    

class RandomSource(object):
    '''
    This signal source is just a random noise.
    '''


    def __init__(self, amplitude=1.0):
        '''
        Constructor
        '''
        