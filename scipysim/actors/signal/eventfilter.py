'''
Created on 2010-04-06

@author: Allan McInnes
'''
from scipysim.actors import Siso, Actor, Channel, Event
import logging
import unittest
from numpy import floor, abs


class EventFilter(Siso):
    '''
    Takes an input signal with values at arbitrary levels, and
    generates a discrete-event signal containing events at the times when
    the input signal crosses into a new quantization level.
    Note: assumes a first-order (linear) signal evolution between input
    events, and computes the output event time accordingly.
    '''
    def __init__(self, input_channel, output_channel, delta=0.5):
        """
        Constructor for an event filter.
        
        @param delta: the quantization step
        """
        super(EventFilter, self).__init__(input_channel=input_channel,     
                                        output_channel=output_channel, 
                                        child_handles_output=True)
        self.delta = delta
        self.current_quantum = None
        self.last_event = Event(0.0, 0.0)

    def siso_process(self, event):
        tag, value = event.tag, event.value
        logging.debug("EventFilter received (tag: %2.e, value: %2.e )" % (tag, value))        
        quantized_value = self.delta * floor(value / self.delta)
        
        if quantized_value != self.current_quantum:
            if self.current_quantum is None:
                # Initial output
                out_event = Event(tag, quantized_value)
            else:
                # Approximate the threshold crossing time by linear interpolation
                signal_gradient = ((value - self.last_event.value) /
                                    (tag - self.last_event.tag))
                event_dt = ((quantized_value  - self.last_event.value) / 
                                signal_gradient)
                event_time = min(self.last_event.tag + event_dt, tag)
                out_event = Event(event_time, quantized_value)
                
            self.output_channel.put(out_event)
            self.current_quantum = quantized_value

        self.last_event = Event(tag, value)
        return

class EventFilterTests(unittest.TestCase):
    '''Test the event-filter actor'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = Channel("CT")
        self.q_out = Channel("DE")

    def test_ramp_event_detection(self):
        '''
        Test event detection on a simple ramp signal.
        '''
        inp = [Event(i/3, i/3) for i in xrange(-60, 63, 1)]
        ef = EventFilter(self.q_in, self.q_out, 2)
        expected_outputs = [Event(i, i) for i in xrange(-20, 21, 2)]
                
        ef.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        ef.join()

        for expected_output in expected_outputs:
            out = self.q_out.get()
            self.assertEquals(out.tag, expected_output.tag)            
            self.assertEquals(out.value, expected_output.value)
        self.assertEquals(self.q_out.get(), None)

if __name__ == "__main__":
    unittest.main()

