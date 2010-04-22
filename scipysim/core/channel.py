'''
Contains the Channel class and helper functions for creating multiple channels.
'''

from Queue import Queue

'''
At present the scipy-sim ensures that events are immutable by copying as they enter a channel.
In future this will change as events will become objects in their own right.
'''
from copy import deepcopy as copy

class Channel(Queue, object):
    '''
    A Channel is based on the Python Queue, used for communicating between Actor threads.
    
    A Channel must be created for a specific domain:
        * CT - Continuous Time
        * DT - Discrete Time
        * DE - Discrete Event
        
    @param domain: The two letter domain code as a string
    '''

    def __init__(self, domain="CT"):
        '''Construct a queue with domain type information.
        
        @param domain: The specific domain of events that this channel will carry.
                        - defaults to "CT" domain.
        '''
        super(Channel, self).__init__()
        self.domain = domain

    def put(self, new_item, *args, **kwargs):
        '''
        Put an item into this channel, ensures immutable by copying.
        '''
        if new_item is not None:
            item = copy(new_item)
        else:
            item = None
        super(Channel, self).put(item, args, kwargs)

def MakeChans(num):
    '''Return a list of n channels.
    
    @param num of channels to create.
    '''
    return [Channel() for i in xrange(num)]
