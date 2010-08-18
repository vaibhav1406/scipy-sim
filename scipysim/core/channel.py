'''
Channel class and helper functions for creating multiple channels.

@author: Allan McInnes
@author: Brian Thorne

'''

from Queue import Queue
from time import time


class Channel(Queue, object):
    '''
    A Channel is based on the Python Queue, used for communicating between
    Actor threads.
    
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
        '''Put an event into the channel.'''
        super(Channel, self).put(item, args, kwargs)

    def head(self, block=True, timeout=None):
        '''Return the event at the head of the channel, but don't remove it.

        Blocks indefinitely when the channel is empty if 'block' is True
        and 'timeout' is None.

        Blocks for 'timeout' seconds when the channel is empty if 'block'
        is True and 'timeout' is a positive number. Raises an Empty exception
        if no item is available on timeout. A negative timeout is equivalent
        to setting 'block' equal to false.

        Raises an Empty exception if the channel is empty and 'block' is false.

        @param block: True if an empty channel should cause blocking.
        @param timeout: number of seconds to wait if blocked.
        
        '''
        self.not_empty.acquire()
        try:
            # Assume block == True is the common case
            if block:
                if timeout is None:
                    while not self._qsize():
                        self.not_empty.wait()
                elif timeout < 0:
                    if not self._qsize():
                        raise Empty
                else:
                    start = time()
                    while not self._qsize():
                        elapsed = time() - start
                        if elapsed >= timeout:
                            raise Empty
                        self.not_empty.wait(timeout - elapsed)
            else:
                if not self._qsize():
                    raise Empty

            return self._head()
        finally:
            self.not_empty.release()

    def drop(self):
        '''Remove the event at the head of the channel.'''
        self.not_empty.acquire()
        try:
            if self._qsize():
                self._drop()
        finally:
            self.not_empty.release()

    # Look at the head of the channel
    def _head(self):
        return self.queue[0]

    # Remove the head of the channel
    def _drop(self):
        del self.queue[0]


def MakeChans(num, domain='CT'):
    '''Return a list of n channels.
    
    @param num: number of channels to create.
    @param domain: The specific domain of events that this channel will carry.
                        - defaults to 'CT' domain.    
    '''
    return [Channel(domain) for i in xrange(num)]
