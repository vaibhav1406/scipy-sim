'''
Events are the primitives from which signals are built. Each event is a 
tag-value pair, with the tags being drawn from a partially ordered or totally 
ordered set. A signal is then a collection of events.

This notion of events as a primitive for signals comes from Lee and
Sangiovanni-Vincentelli's "tagged signal model" of signals and systems.

@see http://ptolemy.eecs.berkeley.edu/papers/96/denotational/denotationalERL.pdf

Created on 16/03/2010

@author: Allan McInnes
@author: Brian Thorne
'''

# For backwards compatibility with dict-based events
from collections import Mapping 

from numpy import inf

class Event(Mapping):
    '''
    An Event consists of a tag (e.g. time in a continuous-time model of
    computation, but may be interpreted in other ways by other models of 
    computation) and a value. An event may be marked as representing
    the last event in a signal by constructing it with 'last' = true.
    
    @note For backwards compatibility with older-style dict-based events, the
    Event class uses the Mapping mixin from collections.
    
    Example of usage:
    
    >>> e = Event(1.0, 3.5)
    >>> e.tag
    1.0
    >>> e.value
    3.5
    >>> e['tag']
    1.0
    >>> e['value']
    3.5
    >>> e.value += 22
    Traceback (most recent call last):
      ...
    TypeError: Events are immutable
    >>> e['tag'] = 1
    Traceback (most recent call last):
      ...
    TypeError: 'Event' object does not support item assignment

    '''
    __event = None 

    def __init__(self, tag=None, value=None, last=False):
        '''
        Construct an immutable event from a tag and a value.
        
        TODO: Could we also allow initialization from a dict?
        
        @param tag
        @param value
        @param last: true if this is the last event in a signal
        '''
        super(Event, self).__setattr__('_Event__event', 
                                       { 'tag':   tag,
                                         'value': value,
                                         'last':   last})
    
    def __repr__(self):
        return 'Event(%s, %s, %s)' % (self.tag, self.value, self.last)
    
    def __iter__(self):
        '''
        Implement Mapping interface to allow Events to behave as dicts
        (for backwards compatibility with earlier Event implementation).
        '''     
        return iter(self.__event)
        
    def __contains__(self, key):
        '''
        Implement Mapping interface to allow Events to behave as dicts
        (for backwards compatibility with earlier Event implementation).
        '''    
        return key in self.__event
    
    def __len__(self):
        '''
        Implement Mapping interface to allow Events to behave as dicts
        (for backwards compatibility with earlier Event implementation).
        ''' 
        return len(self.__event)    
        
    def __getitem__(self, key):
        '''Allow dict-style access for 'tag', 'value', and 'last'.'''
        return self.__event[key]
    
    def __getattr__(self, name):
        '''Allow accessors for 'tag', 'value', and 'last'. '''
        return self.__event[name]    
    
    def __setattr__(self, name, value):
        '''Disable changes to attributes.'''
        self.__mutation_error()
    
    def __delattr__(self, name):
        '''Disable deletion of attributes.'''
        self.__mutation_error()

    def __getstate__(self):
        '''Support for pickling.

        The scheme we use for immutability seems to interfere with
        the pickling protocol. To get around this, we define the __getstate__
        method, and have it return the internal object state.'''
        return self.__event

    def __setstate__(self, state):
        '''Support for unpickling.

        The scheme we use for immutability seems to interfere with
        the pickling protocol. The __setstate__ method, using a state
        assumed to have been returned by Event.__getstate__, ensures that
        the Event internal state is properly reconstructed during unpickling.
        '''
        super(Event, self).__setattr__('_Event__event', state)

    def __mutation_error(self):
        raise TypeError("Events are immutable")
        
    def copy(self):
        '''Return a shallow copy of the Event.'''
        return Event(self.tag, self.value, self.last)
        
    def __copy__(self):
        '''Return a shallow copy of the Event.'''
        return Event(self.tag, self.value, self.last)
        
    def __deepcopy__(self, memo={}):
        '''Return a deep copy of the Event.'''
        from copy import deepcopy
        result = self.__class__()
        memo[id(self)] = result
        copied = deepcopy(self.__event, memo)
        result.__init__(copied['tag'], copied['value'], copied['last'])
        return result    


class LastEvent(Event):
    '''
    An immutable signal termination event with a value of None.

    '''

    def __init__(self, tag=inf):
        '''
        Construct an immutable termination event.
        
        @param tag
        '''
        super(LastEvent, self).__init__(tag, None, True)


# --------------------------------------------------------------------
# Testing
# --------------------------------------------------------------------
if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
    import unittest        
    class TestEvent(unittest.TestCase):
    
        def setUp(self):
            self.tag = 1.1
            self.value = 3.1415927
            self.event = Event(self.tag, self.value)
            
        def test_event_is_readable(self):
            self.assertEqual(self.event.tag, self.tag)
            self.assertEqual(self.event.value, self.value)

        def test_event_is_copyable(self):
            event = self.event.copy()
            self.assertEqual(event.tag, self.tag)
            self.assertEqual(event.value, self.value)

        def test_event_is_a_map(self):
            self.assertEqual(self.event['tag'], self.tag)
            self.assertEqual(self.event['value'], self.value)    
    
        def test_tag_is_immutable(self):
            def mutate():
                self.event.tag = 5.0
            self.assertRaises(TypeError, mutate)
            
        def test_value_is_immutable(self):
            def mutate():
                self.event.value = 5.0            
            self.assertRaises(TypeError, mutate)
            
        def test_event_is_immutable(self):
            def mutate():
                self.event.newfield = "hi"            
            self.assertRaises(TypeError, mutate)            

        def test_event_map_value_is_immutable(self):
            def mutate():
                self.event['tag'] = 5            
            self.assertRaises(TypeError, mutate) 
     
        def test_event_map_is_immutable(self):
            def mutate():
                self.event['aKey'] = 5            
            self.assertRaises(TypeError, mutate)

        def test_event_map_is_picklable(self):
            state = self.event.__getstate__()
            event = Event()
            event.__setstate__(state)
            self.assertEqual(event.tag, self.tag)
            self.assertEqual(event.value, self.value)

        def test_event_is_not_terminal(self):
            self.assertFalse(self.event.last)

            
    class TestLastEvent(unittest.TestCase):

        def setUp(self):
            self.tag = 1.1
            self.event = LastEvent(self.tag)

        def test_event_is_terminal(self):
            self.assertTrue(self.event.last)

        def test_event_is_copyable(self):
            event = self.event.copy()
            self.assertEqual(event.tag, self.tag)
            self.assertEqual(event.value, None)
            self.assertTrue(event.last)

        def test_last_is_immutable(self):
            def mutate():
                self.event.last = False
            self.assertRaises(TypeError, mutate)

    unittest.main()

        
