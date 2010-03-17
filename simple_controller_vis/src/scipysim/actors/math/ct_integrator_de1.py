'''
Created on 21/12/2009

@author: Allan McInnes
'''
from scipysim.actors import Siso
import numpy as np  # Only here for the sign() function at this stage


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
        self.x = init
        self.xdot = 0.0
        self.dx = 0.0
        self.next_t = 0.0     # TODO: should probably make this settable
        self.last_t = self.next_t
        self.delta = delta
        self.maxstep = k * delta
        
        # Generate an initial output
        self.__internal_transition()

    def __timestep(self):
        '''
        The size of the time step is either the amount of
        time it takes to reach the next quantization level given
        the current value of the derivative (assuming a linear projection
        forward in time), or the maximum step size, whichever is smaller.   
        '''
        step = abs(self.dx / self.xdot) if self.xdot != 0.0 else np.inf 
        return min(step, self.maxstep)    
            

    def __internal_transition(self):
        '''
        DEVS-style 'internal transition' occurs when time has advanced
        to the next output instant. They generate both an output
        and a state change.
        '''
        self.x += self.dx 
        self.last_t = self.next_t        
        out_event = {'tag':self.last_t, 'value':self.x}
        
        # Project time to reach next quantization level based on current 
        # derivative. 
        self.dx = self.delta * np.sign(self.xdot)  # Next state increment 
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
        
        # Find the direction of movement
        # dir = 1 implies moving to the next higher quantization level
        # dir = -1 implies moving to the next lower quantization level
        # dir = 0 implies moving back to the last quantization level
        dir = np.sign(np.sign(self.xdot) + np.sign(xdot))

        # Distance to next quantized state given the direction of movement
        self.dx = (self.x - new_x) + dir*self.delta 

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

        # External time has moved past the internal time, so first
        # process 'internal transition' (DEVS terminology)
        while tag >= self.next_t:
            self.__internal_transition()
            
        # Process 'external transition' (DEVS terminology) caused by
        # reception of an input event
        self.__external_transition(tag, xdot)




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
        '''Test a simple integration of xdot = -x.
        '''
        # These tags and values taken from Table 1 of Nutaro's paper. Note that here instead of
        # actually closing the loop around the integrator we're
        # simply feeding in a sequence of values corresponding to the function f(x) = -x, and
        # then later checking that the outputs we get match the inputs we fed in. This allows
        # the testing to be done without relying on other actors.
        intags = [0.0, 0.15, 0.3265, 0.5408, 0.8135, 1.189, 1.789, 3.289, 6.289, 7.789]
        invals = [-1.0, -0.85, -0.7, -0.55, -0.4, -0.25, -0.1, 0.05, -0.1, 0.05]
        inputs = [{'value':val, 'tag':tag} for (val, tag) in zip(invals, intags)]

        expected_output_tags = [0.0, 0.15, 0.3264705, 0.5407857, 0.8135272, 1.1884999, 1.789, 3.289, 6.289, 7.789, 10.789]
        expected_output_values = [1.0, 0.85, 0.7, 0.55, 0.4, 0.25, 0.1, -0.05, 0.1, -0.05, 0.0999999]
        expected_outputs = [{'value':val, 'tag':tag} for (val, tag) in zip(expected_output_values, expected_output_tags)]

        # k has been set to make maxstep 10.0
        block = CTIntegratorDE1(self.q_in, self.q_out, init=1.0, delta=0.15, k=10.0 / 0.15)
        SisoCTTestHelper(self, block, inputs, expected_outputs)

    def test_simple_integration_2(self):
        '''
        Test two simultaneous integrations. 
        Testing using same values as above, but also clones output for 
        second integration.
        '''
        from scipysim.actors.signal import Copier
        # These tags and values taken from Table 1 of Nutaro's paper. Note that here instead of
        # actually closing the loop around the integrator we're
        # simply feeding in a sequence of values corresponding to the function f(x) = -x, and
        # then later checking that the outputs we get match the inputs we fed in. This allows
        # the testing to be done without relying on other actors.
        intags = [0.0, 0.15, 0.3265, 0.5408, 0.8135, 1.189, 1.789, 3.289, 6.289, 7.789]
        invals = [-1.0, -0.85, -0.7, -0.55, -0.4, -0.25, -0.1, 0.05, -0.1, 0.05]
        inputs = [{'value':val, 'tag':tag} for (val, tag) in zip(invals, intags)]

        expected_output_tags = [0.0, 0.15, 0.3264705, 0.5407857, 0.8135272, 1.1884999, 1.789, 3.289, 6.289, 7.789, 10.789]
        expected_output_values = [1.0, 0.85, 0.7, 0.55, 0.4, 0.25, 0.1, -0.05, 0.1, -0.05, 0.0999999]
        expected_outputs = [{'value':val, 'tag':tag} for (val, tag) in zip(expected_output_values, expected_output_tags)]

        q1, q2, q3 = Channel(), Channel(), Channel()

        blocks = [
                    CTIntegratorDE1(self.q_in, self.q_out, init=1.0, delta=0.15, k=10.0 / 0.15),
                    Copier(self.q_out, [q1, q2]),
                    CTIntegratorDE1(q1, q3, init=1.0, delta=0.15)
                  ]

        [self.q_in.put(val) for val in inputs + [None]]

        [b.start() for b in blocks]
        [b.join() for b in blocks]
        for expected_output in expected_outputs:
            out = q2.get()
            print out
            self.assertAlmostEqual(out['value'], expected_output['value'], 6)
            self.assertAlmostEqual(out['tag'], expected_output['tag'], 6)

        self.assertEquals(q2.get(), None)

def quickTest():
    from scipysim.actors.math import Proportional
    from scipysim.actors.signal import Copier

    c1, c2, c3, c4 = Channel(), Channel(), Channel(), Channel()
    
    blocks = [
                CTIntegratorDE1(c1, c2, init=1.0, delta=0.15, k=10/0.15),
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

