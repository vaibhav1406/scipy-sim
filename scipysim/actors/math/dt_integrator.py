'''
Discrete-time integrator.

Three different discrete-time integration algorithms are available:

 * Backward Euler (aka Backward Rectangular)
 * Forward Euler (aka Forward Rectangular)
 * Trapezoidal
 
Note that all three implementations current assume uniform unit intervals between
input time tags.

@author: Brian Thorne
@author: Allan McInnes

Created on 9/12/2009
Additional integration algorithms added 08/02/2010
'''
from scipysim.actors import Actor, Channel, Siso

class DTIntegrator(Siso):
    '''
    Abstract base class for discrete-time integrator blocks.
   '''

    input_domains = ("DT",)
    output_domains = ("DT",)

    def __init__(self, input_channel, output_channel, init=0.0):
        '''
        Constructor for the discrete-time integrator actor. 
        '''
        super(DTIntegrator, self).__init__(input_channel=input_channel,
                                           output_channel=output_channel)

        self.y_old = init  # y[n-1] : the last output
        self.y = init      # y[n] : the output

    def siso_process(self, event):
        event = self.integrate(event)
        return event

    def integrate(self, event):
        '''This method must be overridden. It implements the integration algorithm
        based on the current and previous events.
        @return Event
        '''
        raise NotImplementedError


class DTIntegratorBackwardEuler(DTIntegrator):
    '''Backward Euler (aka Backward Rectangular) discrete-time integration.'''
    def integrate(self, event):
        ''' y[n] = y[n-1] + x[n] '''
        self.y = self.y_old + event['value']
        self.y_old = self.y
        # Generate output event
        out_event = {'tag':event['tag'], 'value':self.y}
        return out_event

class DTIntegratorForwardEuler(DTIntegrator):
    '''Forward Euler (aka Forward Rectangular) discrete-time integration.'''
    def integrate(self, event):
        ''' y[n] = y[n-1] + x[n-1] '''
        self.y = self.y_old
        self.y_old += event['value']
        # Generate output event
        out_event = {'tag':event['tag'], 'value':self.y}
        return out_event


class DTIntegratorTrapezoidal(DTIntegrator):
    '''Trapezoidal discrete-time integration.'''
    def __init__(self, input_channel, output_channel, init=0.0):
        super(DTIntegratorTrapezoidal, self).__init__(input_channel=input_channel,
                                                      output_channel=output_channel)
        self.x_old = 0.0   # x[n] : the last input    

    def integrate(self, event):
        ''' y[n] = y[n-1] + 0.5*(x[n] + x[n-1]) '''
        self.y = self.y_old + 0.5 * (event['value'] + self.x_old)
        self.x_old = event['value']
        self.y_old = self.y
        # Generate output event
        out_event = {'tag':event['tag'], 'value':self.y}
        return out_event



import unittest
class DTIntegratorTests(unittest.TestCase):
    '''Test the integrator actors'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = Channel()
        self.q_out = Channel()

    def test_backward_euler(self):
        '''Test backward Euler integration of a simple positive integer signal.
        '''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 10, 1)]

        expected_output_values = [sum(range(i)) for i in xrange(1, 11)]

        block = DTIntegratorBackwardEuler(self.q_in, self.q_out)
        block.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        block.join()

        for expected_output in expected_output_values:
            out = self.q_out.get()
            self.assertEquals(out['value'], expected_output)
        self.assertEquals(self.q_out.get(), None)

    def test_forward_euler(self):
        '''Test forward Euler integration of a simple positive integer signal.
        '''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 10, 1)]

        expected_output_values = [sum(range(i)) for i in xrange(0, 10)]

        block = DTIntegratorForwardEuler(self.q_in, self.q_out)

        block.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        block.join()

        for expected_output in expected_output_values:
            out = self.q_out.get()
            self.assertEquals(out['value'], expected_output)
        self.assertEquals(self.q_out.get(), None)

    def test_trapezoidal(self):
        '''Test trapezoidal integration of a simple positive integer signal.
        '''
        inp = [{'value':i, 'tag':i} for i in xrange(0, 10, 1)]

        x_avgs = [0.5 * (x + (x - 1)) for x in xrange(1, 11, 1)]
        expected_output_values = [sum(x_avgs[:i]) for i in range(10)]

        block = DTIntegratorTrapezoidal(self.q_in, self.q_out)

        block.start()
        [self.q_in.put(val) for val in inp]
        self.q_in.put(None)
        block.join()

        for expected_output in expected_output_values:
            out = self.q_out.get()
            self.assertEquals(out['value'], expected_output)
        self.assertEquals(self.q_out.get(), None)

if __name__ == "__main__":
    unittest.main()
