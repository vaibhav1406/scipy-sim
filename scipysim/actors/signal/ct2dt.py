
from scipysim.actors import Siso, Channel, Event, LastEvent
import unittest


class Ct2Dt(Siso):
    '''
    Samples a continuous-time signal at a fixed frequency, and outputs a
    corresponding discrete-time signal. Assumes linear interpolation
    between input events to contrust an output event.
    '''
    def __init__(self, input_channel, output_channel, frequency=0.5):
        """
        Constructor

        @param frequency: the sampling frequency in Hz
        """
        assert input_channel.domain == 'CT'
        assert output_channel.domain == 'DT'

        super(Ct2Dt, self).__init__(input_channel=input_channel,
                                    output_channel=output_channel,
                                    child_handles_output=True)
        self.output_frequency = frequency
        self.output_period = 1.0 / frequency
        self.out_tag = 0
        self.last_event = None
        self.next_time = None

    def siso_process(self, event):
        out_event = None
        if self.next_time is None:
            # the first data point
            out_event = Event(self.out_tag, event.value)
            self.next_time = event.tag + self.output_period
        elif self.next_time <= event.tag:
            # the next data point for given frequency
            dt = (event.tag - self.last_event.tag)
            dv = (event.value - self.last_event.value)
            out_value = self.last_event.value + (dv/dt)*(self.next_time - self.last_event.tag)
            out_event = Event(self.out_tag, out_value)
            self.next_time += self.output_period

        self.last_event = event
        if out_event is not None:
            self.out_tag += 1
            self.output_channel.put(out_event)



class Ct2DtTests(unittest.TestCase):
    '''Test the Ct2Dt actor'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = Channel("CT")
        self.q_out = Channel("DT")

    def test_simple_ramp(self):
        '''Convert a simple ramp signal'''
        inp = [Event(value=i, tag=i/10.0) for i in xrange(0, 100, 1)]

        expected_outputs = [Event(value=i*2, tag=i) for i in xrange(0, 50, 1)]

        sampler = Ct2Dt(self.q_in, self.q_out, 5)
        sampler.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(LastEvent())
        sampler.join()

        for expected_output in expected_outputs:
            out = self.q_out.get()
            self.assertAlmostEquals(out.value, expected_output.value)
            self.assertEquals(out.tag, expected_output.tag)
        #self.assertTrue(self.q_out.get().last)


if __name__ == "__main__":
    unittest.main()

