'''
Contains the Channel class and helper functions for creating multiple channels.
'''

from Queue import Queue

class Channel(Queue, object):
    '''
    A Channel is based on the Python Queue, used for communicating between Actor threads.
    
    A Channel must be created for a specific domain, e.g.:
        * CT - Continuous Time
        * DT - Discrete Time
        * DE - Discrete Event
        
    @param domain: The two letter domain code as a string
    '''

    def __init__(self, domain='CT'):
        '''Construct a queue with domain type information.
        
        @param domain: The specific domain of events that this channel will carry.
                        - defaults to 'CT' domain.
        '''
        super(Channel, self).__init__()
        self.domain = domain

    def put(self, item, *args, **kwargs):
        '''
        Put an item into this channel.
        '''
        super(Channel, self).put(item, args, kwargs)


def MakeChans(num, domain='CT'):
    '''Return a list of n channels.
    
    @param num of channels to create.
    @param domain: The specific domain of events that this channel will carry.
                        - defaults to 'CT' domain.    
    '''
    return [Channel(domain) for i in xrange(num)]
