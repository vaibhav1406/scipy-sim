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

class Event(object):
    '''
    An Event consists of a tag (e.g. time in a continuous-time model of
    computation, but may be interpreted in other ways by other models of 
    computation) and a value.
    
    Example of usage:
    
    >>> e = Event(1.0, 3.5)
    >>> e.tag
    1.0
    >>> e.value
    3.5
    >>> e.value += 22
    Traceback (most recent call last):
      ...
    TypeError: Events are immutable
    
    '''
    __event = None 

    def __init__(self, tag=None, value=None):
        '''
        Construct an immutable event from a tag and a value.
        
        @param tag
        @param value
        '''
        super(Event, self).__setattr__('_Event__event', 
                                       { 'tag': tag, 'value': value })
    
    def __getattr__(self, name):
        '''
        Allow accessors for 'tag' and 'value'. 
        '''
        return self.__event[name]    
    
    def __setattr__(self, name, value):
        '''Disable changes to attributes.'''
        self.__mutation_error()
    
    def __delattr__(self, name):
        '''Disable deletion of attributes.'''
        self.__mutation_error()
    
    def __mutation_error(self):
        raise TypeError("Events are immutable")
        
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
            
    unittest.main()

        