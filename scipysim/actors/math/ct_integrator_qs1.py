'''
********************************************************************************

                    !!!! CAUTION !!!!

  Highly experimental. In a constant state of flux. Filled with horrible hacks.
  Possibly broken. Likely buggy. Do not use unless you know what you're getting
  in to.

********************************************************************************

@author: Allan McInnes
'''
from scipysim.actors import Siso, Event, LastEvent
import numpy as np  


class CTIntegratorQS1(Siso):
    '''
    A SISO first-order continuous-time integrator that uses a quantized-state
    approach to integration (rather than the traditional discrete-time
    approach). In this approach we discretize the system state instead of the
    value of time, and consequently take variable-sized time steps that are 
    matched to the rate of change of the integrated function.
    
    See:
    James Nutaro, "Discrete-Event Simulation of Continuous Systems", in
    Handbook of Dynamic System Modeling (Paul Fishwick Ed.)
    Francois Cellier and Ernesto Kofman "Continuous System Simulation", 
    Chapter 11: "Discrete-Event Simulation".
    '''

    input_domains = ('CT',)
    output_domains = ('CT',)

    def __init__(self, xdot, x, init=0.0, delta=0.1, maxstep=1, algebraic_loop=False):
        '''
        Construct a SISO CT integrator.
        
        @param xdot: input signal to be integrated
        @param x: output integral
        @param init: the initial state of the integral
        @param delta: the state quantization step-size
        @param maxstep: maximum allowable timestep
        '''
        super(CTIntegratorQS1, self).__init__(input_channel=xdot,
                                              output_channel=x,
                                              child_handles_output=True)
                                              
        self.delta = delta
        self.maxstep = maxstep
        self.x = init
        self.xdot = 0.0      # TODO: make this configurable
        self.qx = self.__quantize(init)
        self.dx = 0.0
        self.next_t = 0.0     # TODO: should probably make this configurable
        self.last_t = self.next_t
        self.algebraic_loop = algebraic_loop

        self.last_dt_out_t = 0.0
        self.discrete_time = False

        # Generate an initial output
        self.__internal_transition()

    def __quantize(self, x):
        return self.delta * np.rint(x / self.delta)
        
    def __statestep(self):
        return self.qx + np.sign(self.xdot)*self.delta/2.0 - self.x

    def __timestep(self):
        '''
        The size of the time step is either the amount of
        time it takes to reach the next quantization level given
        the current value of the derivative (assuming a linear projection
        forward in time), or the time it takes to reach a point that will 
        ensure outputs are no more than the maximum step size apart,
        whichever is smaller.
        '''
        if self.xdot != 0.0: # and self.dx > 100.0 * np.finfo(np.float_).resolution:
            de_step = np.fabs(self.dx / self.xdot)
        else:
            de_step = np.inf

        step = min(de_step, (self.last_dt_out_t + self.maxstep) - self.last_t)
        self.discrete_time = (step != de_step)
        return step
            

    def __internal_transition(self):
        '''
        DEVS-style 'internal transitions' occur when time has advanced
        to the next output instant. They generate both an output
        and a state change.
        '''
        elapsed = self.next_t - self.last_t
        self.last_t = self.next_t

        if self.discrete_time:
            self.x += self.xdot * elapsed
            self.qx = self.__quantize(self.x)
            self.last_dt_out_t = self.last_t
        else:
            self.x = self.qx + np.sign(self.xdot)*self.delta/2.0
            self.qx += np.sign(self.xdot)*self.delta
        
        # Project time to reach next quantization level based on current 
        # derivative.         
        self.dx = self.__statestep()
        self.next_t += self.__timestep()           # Next output time

        self.output_channel.put( Event(self.last_t, self.qx) )

        
        
    def __external_transition(self, tag, xdot):
        '''
        DEVS-style external transitions occur in response to 
        received events. They do not generate an output, only
        a state change (which may trigger an output on the next
        internal transition)
        
        @param tag: tag of the triggering event
        @param xdot: value of the triggering event
        '''
        elapsed = tag - self.last_t
        # The new value of x must be between quantization levels, since 
        # since tag < self.next_t, and self.next_t indicates the time
        # at which the next quantization level would be reached given
        # a derivative of self.xdot.
        self.x = self.x + self.xdot * elapsed
        self.xdot = xdot
        self.last_t += elapsed

        # Find the change in x required to reach the next quantization level
        # from the new intermediate state
        self.dx = self.__statestep()
        self.next_t = self.last_t + self.__timestep()  # Next output time


    def __str__(self):
        '''
        Converts the current integrator state to a string.
        '''
        s = "["
        s += "last_t:" + str(self.last_t) + ", "        
        s += "next_t:" + str(self.next_t) + ", "        
        s += "x:" + str(self.x) + ", "
        s += "xdot:" + str(self.xdot) + ", "
        s += "dx:" + str(self.dx) + ", "
        s += "qx:" + str(self.qx) + ", "
        s += "last_out:" + str(self.last_out)
        s += "]"
        return s 

    def siso_process(self, event):
        '''
        React to the newest received event.
        
        @param event: event from the input channel 
        '''
        tag, xdot = event.tag, event.value

        # The following is one option for breaking causality problems
        # with algebraic loops        
        if self.algebraic_loop and np.fabs(tag - self.last_t) < 100.0 * np.finfo(np.float_).resolution:
            # We assume that a nearly identical time to the previous event
            # indicates that the only thing advancing time is the integrator
            # itself. This is a bit of a hack, and doesn't work properly if
            # there are other sources of time information entering the loop.
            self.__external_transition(tag, xdot)
            self.__internal_transition()
        else:

            # External time has moved past the internal time, so first
            # process 'internal transition' (DEVS terminology) to bring
            # the integrator up-to-date
            while tag >= self.next_t:
                self.__internal_transition()

            # Process 'external transition' (DEVS terminology) caused by
            # reception of an input event
            self.__external_transition(tag, xdot)

import unittest
from scipysim.actors import SisoCTTestHelper, Channel

class CTintegratorQSTests(unittest.TestCase):
    '''Test the integrator actor'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = Channel()
        self.q_out = Channel()

    def test_simple_integration(self):
        '''
        Test a simple integration of xdot = -x.
        '''
        # Note that here instead of actually closing the loop around the 
        # integrator we're simply feeding in a sequence of values corresponding 
        # to the function f(x) = -x, and then later checking that the outputs we 
        # get match the inputs we fed in. This allows the testing to be done 
        # without relying on other actors.
        intags = [0.0, 0.0500000000000000, 0.1611111111111, 0.28611111111111, 0.42896825396825566, 0.59563492063492, 0.79563492063492, 1.04563492063492, 1.37896825396825, 1.878968253968261, 2.878968253968262]
        invals = [-1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.0]
        inputs = [Event(value=val, tag=tag) for (val, tag) in zip(invals, intags)]

        expected_output_tags = [0.0, 0.0500000000000000, 0.1611111111111, 0.28611111111111, 0.42896825396825566, 0.59563492063492, 0.79563492063492, 1.04563492063492, 1.37896825396825, 1.878968253968261, 2.878968253968262, 10.0]
        expected_output_values = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0, 0.1]
        expected_outputs = [Event(value=val, tag=tag) for (val, tag) in zip(expected_output_values, expected_output_tags)]

        # k has been set to make maxstep 10.0
        block = CTIntegratorQS1(self.q_in, self.q_out, init=1.0, delta=0.1, maxstep=10.0, algebraic_loop=True)
        SisoCTTestHelper(self, block, inputs, expected_outputs)

    def test_simple_integration_2(self):
        '''
        Test two simultaneous integrations. 
        Testing using same values as above, but also clones output for 
        second integration.
        '''
        from scipysim.actors.signal import Split
        # Note that here instead of actually closing the loop around the 
        # integrator we're simply feeding in a sequence of values corresponding 
        # to the function f(x) = -x, and then later checking that the outputs we 
        # get match the inputs we fed in. This allows the testing to be done 
        # without relying on other actors.
        intags = [0.0, 0.0500000000000000, 0.1611111111111, 0.28611111111111, 0.42896825396825566, 0.59563492063492, 0.79563492063492, 1.04563492063492, 1.37896825396825, 1.878968253968261, 2.878968253968262]
        invals = [-1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.0]
        inputs = [Event(value=val, tag=tag) for (val, tag) in zip(invals, intags)]

        expected_output_tags = [0.0, 0.0500000000000000, 0.1611111111111, 0.28611111111111, 0.42896825396825566, 0.59563492063492, 0.79563492063492, 1.04563492063492, 1.37896825396825, 1.878968253968261, 2.878968253968262, 10.0]
        expected_output_values = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0, 0.1]
        expected_outputs = [Event(value=val, tag=tag) for (val, tag) in zip(expected_output_values, expected_output_tags)]

        q1, q2, q3 = Channel(), Channel(), Channel()

        blocks = [
                    CTIntegratorQS1(self.q_in, self.q_out, init=1.0, delta=0.1, maxstep=10.0, algebraic_loop=True),
                    Split(self.q_out, [q1, q2]),
                    CTIntegratorQS1(q1, q3, init=1.0, delta=0.1, maxstep=10.0, algebraic_loop=True)
                  ]

        [self.q_in.put(val) for val in inputs + [LastEvent()]]

        [b.start() for b in blocks]
        [b.join() for b in blocks]
        for expected_output in expected_outputs:
            out = q2.get()
            self.assertAlmostEqual(out.value, expected_output.value, 4)
            self.assertAlmostEqual(out.tag, expected_output.tag, 4)

        self.assertTrue(q2.get().last)

if __name__ == '__main__':
    unittest.main()

