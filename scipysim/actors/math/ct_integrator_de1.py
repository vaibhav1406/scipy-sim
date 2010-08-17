'''
Created on 21/12/2009

@author: Allan McInnes
'''
from scipysim.actors import Siso
import numpy as np  


class CTIntegratorDE1(Siso):
    '''
    A SISO first-order continuous-time integrator that uses a discrete-event
    approach to integration (rather than the traditional discrete-time
    approach). In this approach we quantize the system state instead of the
    value of time, and consequently take variable-sized time steps that are 
    matched to the rate of change of the integrated function.
    
    See:
    James Nutaro, "Discrete-Event Simulation of Continuous Systems", in
    Handbook of Dynamic System Modeling (Paul Fishwick Ed.)
    Francois Cellier and Ernesto Kofman "Continuous System Simulation", 
    Chapter 11: "Discrete-Event Simulation".
    '''

    input_domains = ("CT",)
    output_domains = ("CT",)

    def __init__(self, xdot, x, init=0.0, delta=0.1, k=10.0):
        '''
        Construct a SISO CT integrator.
        
        @param xdot: input signal to be integrated
        @param x: output integral
        @param init: the initial state of the integral
        @param delta: the state quantization step-size
        @param k: coefficient for the maximum allowable timestep (k*delta)
        '''
        super(CTIntegratorDE1, self).__init__(input_channel=xdot,
                                              output_channel=x,
                                              child_handles_output=True)
                                              
        self.delta = delta
        self.maxstep = k * delta
        self.x = init
        self.xdot = -1.0      # TODO: make this configurable
        self.dx = 0
        self.next_t = 0.0     # TODO: should probably make this configurable
        self.last_t = self.next_t

        # Generate an initial output
        self.__internal_transition()

    def __quantize(self, x):
        return self.delta * np.floor(x / self.delta)
        
    def __statestep(self, x, xdot):
        qx = self.__quantize(x)
        dist = (x - qx) if abs(x - qx) > 1e-15 else 0  # Enforce a minimum step - is this like Kofman's hysteresis?
        dist = dist if abs(self.delta - dist) > 1e-15 else 0  # Enforce a minimum step - is this like Kofman's hysteresis?
        if xdot > 0:
            step = self.delta - dist
        elif xdot < 0:
            step = -dist if dist != 0 else -self.delta
        else:
            step = 0
        return step

    def __timestep(self):
        '''
        The size of the time step is either the amount of
        time it takes to reach the next quantization level given
        the current value of the derivative (assuming a linear projection
        forward in time), or the maximum step size, whichever is smaller.   
        '''
        if self.xdot != 0.0 and self.dx != 0.0:
            step = abs(self.dx / self.xdot)
        else:
            step = np.inf 
        return min(step, self.maxstep)   
            

    def __internal_transition(self):
        '''
        DEVS-style 'internal transition' occurs when time has advanced
        to the next output instant. They generate both an output
        and a state change.
        '''    
        self.x += self.dx 
        self.last_t = self.next_t        

        # Quantize here in case the actual state is the result
        # of taking a max_step, and has left us between quantum levels    
        out_event = {'tag':self.last_t, 'value':self.__quantize(self.x)}
        #print out_event
        
        # Project time to reach next quantization level based on current 
        # derivative.         
        self.dx = self.__statestep(self.x, self.xdot)
        self.next_t += self.__timestep()           # Next output time

        self.output_channel.put( out_event )

        
        
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
        new_x = self.x + self.xdot * elapsed
        
        # Find the change in x required to reach the next quantization level
        # from the new intermediate state
        self.dx = self.__statestep(new_x, xdot)

        # Update the state
        self.xdot = xdot          
        self.last_t += elapsed  
        self.next_t = self.last_t + self.__timestep()  # Next output time
        self.x = new_x


    def __str__(self):
        '''
        Converts the current integrator state to a string.
        '''
        s = "["
        s += "last_t:" + str(self.last_t) + ", "        
        s += "next_t:" + str(self.next_t) + ", "        
        s += "x:" + str(self.x) + ", "
        s += "xdot:" + str(self.xdot) + ", "
        s += "dx:" + str(self.dx)        
        s += "]"
        return s 

    def siso_process(self, event):
        '''
        React to the newest received event.
        
        @param event: event from the input channel 
        '''
        tag, xdot = event['tag'], event['value']

        if abs(tag - self.last_t) < 1e-15:
            # We assume that a nearly identical time to the previous event
            # indicates that the only thing advancing time is the integrator
            # itself. Note that this will fail if there's a delay in the
            # loop
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

        #if self.next_t > 20:
        #    self.output_channel.put(None)


import unittest
from scipysim.actors import SisoCTTestHelper, Channel

class CTintegratorTest(unittest.TestCase):
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
        intags = [0.0, 0.10000000000000001, 0.21111111111111114, 0.33611111111111114, 0.47896825396825399, 0.64563492063492067, 0.84563492063492074, 1.0956349206349207, 1.428968253968254, 1.928968253968254, 2.9289682539682538, 12.928968253968254]
        invals = [-1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.0]
        inputs = [{'value':val, 'tag':tag} for (val, tag) in zip(invals, intags)]

        expected_output_tags = [0.0, 0.10000000000000001, 0.21111111111111114, 0.33611111111111114, 0.47896825396825399, 0.64563492063492067, 0.84563492063492074, 1.0956349206349207, 1.428968253968254, 1.928968253968254, 2.9289682539682538, 12.928968253968254, 22.928968253968254]
        expected_output_values = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0, 0.0, 0.0]
        expected_outputs = [{'value':val, 'tag':tag} for (val, tag) in zip(expected_output_values, expected_output_tags)]

        # k has been set to make maxstep 10.0
        block = CTIntegratorDE1(self.q_in, self.q_out, init=1.0, delta=0.1, k=10.0 / 0.1)
        SisoCTTestHelper(self, block, inputs, expected_outputs)

    def test_simple_integration_2(self):
        '''
        Test two simultaneous integrations. 
        Testing using same values as above, but also clones output for 
        second integration.
        '''
        from scipysim.actors.signal import Copier
        # Note that here instead of actually closing the loop around the 
        # integrator we're simply feeding in a sequence of values corresponding 
        # to the function f(x) = -x, and then later checking that the outputs we 
        # get match the inputs we fed in. This allows the testing to be done 
        # without relying on other actors.
        intags = [0.0, 0.10000000000000001, 0.21111111111111114, 0.33611111111111114, 0.47896825396825399, 0.64563492063492067, 0.84563492063492074, 1.0956349206349207, 1.428968253968254, 1.928968253968254, 2.9289682539682538, 12.928968253968254]
        invals = [-1, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.0]
        inputs = [{'value':val, 'tag':tag} for (val, tag) in zip(invals, intags)]

        expected_output_tags = [0.0, 0.10000000000000001, 0.21111111111111114, 0.33611111111111114, 0.47896825396825399, 0.64563492063492067, 0.84563492063492074, 1.0956349206349207, 1.428968253968254, 1.928968253968254, 2.9289682539682538, 12.928968253968254, 22.928968253968254]
        expected_output_values = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0, 0.0, 0.0]
        expected_outputs = [{'value':val, 'tag':tag} for (val, tag) in zip(expected_output_values, expected_output_tags)]

        q1, q2, q3 = Channel(), Channel(), Channel()

        blocks = [
                    CTIntegratorDE1(self.q_in, self.q_out, init=1.0, delta=0.1, k=10.0 / 0.1),
                    Copier(self.q_out, [q1, q2]),
                    CTIntegratorDE1(q1, q3, init=1.0, delta=0.1, k=10.0 / 0.1)
                  ]

        [self.q_in.put(val) for val in inputs + [None]]

        [b.start() for b in blocks]
        [b.join() for b in blocks]
        for expected_output in expected_outputs:
            out = q2.get()
            #print out
            self.assertAlmostEqual(out['value'], expected_output['value'], 4)
            self.assertAlmostEqual(out['tag'], expected_output['tag'], 4)

        self.assertEquals(q2.get(), None)

def quickTest():
    from scipysim.actors.math import Proportional
    from scipysim.actors.signal import Copier

    c1, c2, c3, c4 = Channel(), Channel(), Channel(), Channel()
    
    blocks = [
                CTIntegratorDE1(c1, c2, init=1.0, delta=0.1, k=10/0.1),
                Copier(c2, [c3, c4]),
                Proportional(c3, c1, -1.0),
             ]
    
    [b.start() for b in blocks]
    [b.join() for b in blocks]
    out = c4.get()
    while not out is None :
        out = c4.get()

if __name__ == '__main__':
    unittest.main()
    #quickTest()

