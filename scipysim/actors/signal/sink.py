'''
Sink 
@author Allan McInnes
'''
from scipysim.actors import Actor, Channel, Event, LastEvent
import logging
import unittest

class Sink(Actor):
    '''
    Acts as a sink for events, accepting any kind of event from a single 
    channel, and simply discarding it. This provides a way to terminate 
    otherwise unconnected output ports.
    '''
    num_inputs = 1
    num_outputs = 0
    
    def __init__(self, input):
        """
        Constructor for a sink.
        
        @param input: the channel to receive events from.
        """
        super(Sink, self).__init__(input_channel=input, 
                                   output_channel=None)

    def process(self):
        """This gets called by the Actor parent.
        It will look at the input channel - if the channel contains "None"
        the actor is stopped. Otherwise the new Event is popped off
        the channel and discarded.
        """
        event = self.input_channel.get(True)     # this is blocking
        if event.last:
            logging.info('Sink process is finished.')
            self.stop = True
            return
            
        logging.debug("Sink received (tag: %2.e, value: %2.e )" % (event.tag, event.value))
        return

class SinkTests(unittest.TestCase):
    '''Test the sink actor'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = Channel()

    def test_sink(self):
        '''Test that sink runs.
        '''
        inp = [Event(i,i) for i in xrange(0, 100, 1)]

        try:
            sink = Sink(self.q_in)
            sink.start()
            [self.q_in.put(val) for val in inp]
            self.q_in.put(LastEvent())
            sink.join()
        except:
            self.fail("Sink failed to run without exception.")


if __name__ == "__main__":
    unittest.main()
