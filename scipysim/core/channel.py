'''
Channel class and helper functions for creating multiple channels.

@author: Allan McInnes
@author: Brian Thorne

'''

from Queue import Queue
from Queue import Empty as QEmpty


class Channel(object):
    '''
    A Channel is used for communicating between Actors. Channels are
    FIFO streams of Events.

    A Channel must be created for a specific domain, e.g.:
        * CT - Continuous Time
        * DT - Discrete Time
        * DE - Discrete Event

    @param domain: The two letter domain code as a string

    '''

    class Empty(Exception):
        "Exception raised by Channel.get()."
        pass

    def __init__(self, domain='CT', name=''):
        '''Construct a queue with domain type information.

        @param domain: The specific domain of events that this channel will carry.
                        - defaults to 'CT' domain.
        '''
        super(Channel, self).__init__()
        self.queue = Queue()
        self.domain = domain
        self.name = name
        self._head = None


    def put(self, item, block=True, timeout=None):
        '''Put an event into the channel.       '''
        self.queue.put(item, block=block, timeout=timeout)

    def get(self, block=True, timeout=None):
        '''Get an event from the channel.

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
        if self._head is not None:
            item = self._head
            self._head = None
        else:
            try:
                item = self.queue.get(block=block, timeout=timeout)
            except QEmpty:
                raise self.Empty
        return item

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
        if self._head is None:
            try:
                self._head = self.queue.get(block=block, timeout=timeout)
            except QEmpty:
                raise self.Empty
        return self._head

    def drop(self):
        '''Remove the event at the head of the channel.'''
        if self._head is None:
            try:
                self._head = self.queue.get(block=False)
            except QEmpty:
                pass
        self._head = None

    def empty(self):
        return self._head is None and self.queue.empty()


def MakeChans(num, domain='CT'):
    '''Return a list of n channels.

    @param num: number of channels to create.
    @param domain: The specific domain of events that these channels will carry.
                        - defaults to 'CT' domain.
    '''
    return [Channel(domain) for _ in xrange(num)]


def MakeNamedChans(names, domain='CT'):
    '''Return a dict of channels corresponding to the provided names.

    @param names: names of the channels to create.
    @param domain: The specific domain of events that this channel will carry.
                        - defaults to 'CT' domain.
    '''
    return dict( zip( names, MakeChans( len( names ) ) ) )


