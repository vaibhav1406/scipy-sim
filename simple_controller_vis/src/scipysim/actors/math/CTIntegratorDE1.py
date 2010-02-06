'''
Created on 21/12/2009

@author: allan
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
    
    See James Nutaro, "Discrete-Event Simulation of Continuous Systems", in
    Handbook of Dynamic System Modeling (Paul Fishwick Ed.)
    '''
    
    input_domains = ("CT",)
    output_domains = ("CT",)
    
    def __init__(self, xdot, x, init=0.0, delta=0.1, maxstep=10.0):
        '''
        Construct a SISO CT integrator.
        
        @param xdot: input signal to be integrated
        @param x: output integral
        @param init: the initial state of the integral
        @param delta: the state quantization step-size
        @param maxstep: maximum allowable timestep
        '''
        super(CTIntegratorDE1, self).__init__(input_queue=xdot,
                                     output_queue=x)
        self.state = init
        self.delta = delta
        self.maxstep = maxstep
        
        # Generate an initial output
        x.put({'value':init, 'tag':0.0})
        

    def siso_process(self, event):
        xdot = event['value']
        
        # The size of the time step is either the amount of
        # time it takes to cover one state quantization step given
        # the current value of the derivative (assuming a linear projection
        # forward in time), or the maximum step size, whichever is smaller.
        if (abs(xdot) * self.maxstep) < self.delta:
            timestep = self.maxstep
        else:
            timestep = self.delta / abs(xdot)
            
        # State update done this way ensures that we move in steps of exactly delta
        self.state += self.delta * np.sign(xdot)  
        
        # Generate output event
        event['tag'] += timestep
        event['value'] = self.state

        return event


import unittest
import Queue as queue
from scipysim.actors import SisoCTTestHelper
    
class CTintegratorTest(unittest.TestCase):
    '''Test the integrator actor'''

    def setUp(self):
        '''
        Unit test setup code
        '''
        self.q_in = queue.Queue()
        self.q_out = queue.Queue()

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
        inputs = [{'value':val, 'tag':tag} for (val,tag) in zip(invals, intags)]

        expected_output_tags = [0.0, 0.15, 0.3264705, 0.5407857, 0.8135272, 1.1884999, 1.789, 3.289, 6.289, 7.789, 10.789]
        expected_output_values = [1.0, 0.85, 0.7, 0.55, 0.4, 0.25, 0.1, -0.05, 0.1, -0.05, 0.0999999]
        expected_outputs = [{'value':val, 'tag':tag} for (val,tag) in zip(expected_output_values, expected_output_tags)]

        block = CTIntegratorDE1(self.q_in, self.q_out, init=1.0, delta=0.15)
        SisoCTTestHelper(self, block, inputs, expected_outputs)
        
if __name__ == '__main__':
    unittest.main()
        
